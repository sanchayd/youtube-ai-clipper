"""
AWS Transcribe service for real speech-to-text transcription.
"""
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSTranscribeService:
    """Service for transcribing audio using AWS Transcribe."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize AWS Transcribe service.
        
        Args:
            bucket_name: S3 bucket for audio files. If None, gets from environment.
        """
        self.bucket_name = bucket_name or os.getenv('TRANSCRIPTION_BUCKET')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not self.bucket_name:
            raise ValueError("TRANSCRIPTION_BUCKET environment variable not set")
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.transcribe_client = boto3.client('transcribe', region_name=self.region)
        
        logger.info(f"AWS Transcribe service initialized with bucket: {self.bucket_name}")
    
    def transcribe_audio_file(self, audio_file_path: str, video_id: str) -> Dict[str, Any]:
        """
        Transcribe an audio file using AWS Transcribe.
        
        Args:
            audio_file_path: Path to local audio file
            video_id: YouTube video ID for naming
            
        Returns:
            Transcription result with segments and timestamps
        """
        job_name = f"transcribe-{video_id}-{uuid.uuid4().hex[:8]}"
        s3_key = f"audio/{video_id}/{job_name}.mp3"
        
        try:
            # Step 1: Upload audio file to S3
            logger.info(f"Uploading audio file to S3: {s3_key}")
            self._upload_to_s3(audio_file_path, s3_key)
            
            # Step 2: Start transcription job
            logger.info(f"Starting transcription job: {job_name}")
            job_uri = f"s3://{self.bucket_name}/{s3_key}"
            self._start_transcription_job(job_name, job_uri)
            
            # Step 3: Wait for completion (with timeout)
            logger.info("Waiting for transcription to complete...")
            result = self._wait_for_completion(job_name, timeout_seconds=120)
            
            # Step 4: Get and parse results
            transcript_data = self._get_transcription_results(job_name)
            
            # Step 5: Cleanup
            self._cleanup_job_and_files(job_name, s3_key)
            
            return transcript_data
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            # Cleanup on failure
            try:
                self._cleanup_job_and_files(job_name, s3_key)
            except:
                pass
            raise
    
    def _upload_to_s3(self, file_path: str, s3_key: str):
        """Upload file to S3."""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"Successfully uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    def _start_transcription_job(self, job_name: str, job_uri: str):
        """Start AWS Transcribe job."""
        try:
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat='mp3',
                LanguageCode='en-US',
                Settings={
                    'ShowSpeakerLabels': False,  # Simplified for single speaker
                    'MaxSpeakerLabels': 1,
                    'ChannelIdentification': False
                },
                OutputBucketName=self.bucket_name,
                OutputKey=f"transcripts/{job_name}.json"
            )
            logger.info(f"Transcription job started: {job_name}")
        except ClientError as e:
            raise Exception(f"Failed to start transcription job: {str(e)}")
    
    def _wait_for_completion(self, job_name: str, timeout_seconds: int = 120) -> Dict:
        """Wait for transcription job to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                logger.info(f"Job {job_name} status: {status}")
                
                if status == 'COMPLETED':
                    return response['TranscriptionJob']
                elif status == 'FAILED':
                    failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown')
                    raise Exception(f"Transcription job failed: {failure_reason}")
                
                # Wait before next check
                time.sleep(5)
                
            except ClientError as e:
                raise Exception(f"Error checking job status: {str(e)}")
        
        raise Exception(f"Transcription job timed out after {timeout_seconds} seconds")
    
    def _get_transcription_results(self, job_name: str) -> Dict[str, Any]:
        """Download and parse transcription results."""
        try:
            # Download transcript JSON from S3
            transcript_key = f"transcripts/{job_name}.json"
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=transcript_key
            )
            
            import json
            transcript_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Parse AWS Transcribe format to our format
            return self._parse_aws_transcript(transcript_data)
            
        except ClientError as e:
            raise Exception(f"Failed to get transcription results: {str(e)}")
    
    def _parse_aws_transcript(self, aws_data: Dict) -> Dict[str, Any]:
        """Parse AWS Transcribe output to our standard format."""
        try:
            results = aws_data['results']
            transcript_text = results['transcripts'][0]['transcript']
            
            # Parse items into segments
            segments = []
            current_segment = []
            current_start = None
            
            for item in results['items']:
                if item['type'] == 'pronunciation':
                    if current_start is None:
                        current_start = float(item['start_time'])
                    
                    current_segment.append(item['alternatives'][0]['content'])
                    
                    # Create segment every ~5 seconds or 10 words
                    if (len(current_segment) >= 10 or 
                        (item.get('end_time') and 
                         float(item['end_time']) - current_start >= 5.0)):
                        
                        if current_segment:
                            segments.append({
                                "start": current_start,
                                "end": float(item.get('end_time', current_start + 5.0)),
                                "text": ' '.join(current_segment)
                            })
                            current_segment = []
                            current_start = None
            
            # Add remaining words as final segment
            if current_segment and current_start is not None:
                segments.append({
                    "start": current_start,
                    "end": current_start + 5.0,  # Estimate
                    "text": ' '.join(current_segment)
                })
            
            return {
                "text": transcript_text,
                "segments": segments,
                "language": "en-US",
                "duration": segments[-1]["end"] if segments else 0,
                "source": "aws_transcribe"
            }
            
        except Exception as e:
            logger.error(f"Error parsing AWS transcript: {str(e)}")
            raise Exception(f"Failed to parse transcription results: {str(e)}")
    
    def _cleanup_job_and_files(self, job_name: str, audio_s3_key: str):
        """Clean up transcription job and temporary files."""
        try:
            # Delete transcription job
            self.transcribe_client.delete_transcription_job(
                TranscriptionJobName=job_name
            )
            logger.info(f"Deleted transcription job: {job_name}")
        except ClientError:
            logger.warning(f"Could not delete transcription job: {job_name}")
        
        try:
            # Delete audio file from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=audio_s3_key
            )
            logger.info(f"Deleted audio file: {audio_s3_key}")
        except ClientError:
            logger.warning(f"Could not delete audio file: {audio_s3_key}")
        
        try:
            # Delete transcript file from S3
            transcript_key = f"transcripts/{job_name}.json"
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=transcript_key
            )
            logger.info(f"Deleted transcript file: {transcript_key}")
        except ClientError:
            logger.warning(f"Could not delete transcript file: {transcript_key}")
