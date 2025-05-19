# src/services/clip_generator/ffmpeg_service.py
import os
import logging
import ffmpeg
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ClipGenerator:
    def __init__(self, output_dir="/tmp/clips"):
        """Initialize with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_clip(self, video_path: str, start_time: float, 
                      end_time: float, output_name: str = None) -> str:
        """
        Generate a video clip from the specified start and end times.
        Returns the path to the generated clip.
        """
        if not output_name:
            output_name = f"clip_{start_time:.1f}_{end_time:.1f}.mp4"
        
        output_path = os.path.join(self.output_dir, output_name)
        
        logger.info(f"Generating clip from {start_time:.2f}s to {end_time:.2f}s")
        
        try:
            # Use ffmpeg to extract the clip
            (
                ffmpeg
                .input(video_path, ss=start_time, to=end_time)
                .output(output_path, codec='copy')
                .run(quiet=True, overwrite_output=True)
            )
            
            logger.info(f"Clip generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating clip: {str(e)}")
            raise
    
    def generate_clips_from_mentions(self, video_path: str, 
                                     mentions: List[Dict[str, Any]], 
                                     padding_seconds: float = 2.0) -> List[str]:
        """
        Generate clips for each mention, adding padding before and after.
        Returns a list of paths to the generated clips.
        """
        clip_paths = []
        
        for i, mention in enumerate(mentions):
            # Add padding before and after the mention
            start_time = max(0, mention["start"] - padding_seconds)
            end_time = mention["end"] + padding_seconds
            
            # Generate a clip for this mention
            clip_path = self.generate_clip(
                video_path, 
                start_time, 
                end_time, 
                output_name=f"clip_{i+1}.mp4"
            )
            
            clip_paths.append(clip_path)
        
        return clip_paths