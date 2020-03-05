# -*- coding: utf-8 -*-
import os, logging, random, moviepy
from moviepy.video.tools.segmenting import findObjects
import numpy as np
from moviepy.editor import *
from proglog import ProgressBarLogger
from app import socketio

@socketio.on('connect')                                                         
def connect(): 
    print("socket connected") 
    
class ProgressHandler(ProgressBarLogger):
    def callback(self, **changes):
        try:
            socketio.emit('message', {'percent': int(round(self.state['bars'].get('t')['index'])/(int(self.state['bars'].get('t')['total'])/100))})
            # print(int(self.state['bars'].get('t')['index'])/(int(self.state['bars'].get('t')['total'])/100))
        except Exception:
            print("not video writing")
            
class Generator:
    def __init__(self, phrase="TEST", 
                 fontsize=45, 
                 kerning=3, 
                 text_color='white', 
                 font_name='Arial',
                 output_text_filename='output_text.mp4',
                 videoname="video.mp4",
                 logo_filename="/workspace/logo.mp4",
                 fade_out_time=1,
                 fade_in_time=1,
                 time_between_videos=1,
                 output_path = "/workspace/output/",
                 output_fps=25,
                 output_codec='libx264',
                 output_video_width=1280,
                 output_video_height=720,
                 video_bitrate="5000k",
                 input_path="/workspace/videos/"):
        
      self.logger = ProgressHandler()
      self.phrase = '\n'.join(phrase [i:i+37] for i in range(0, len(phrase ), 37))
      self.fontsize = fontsize
      self.kerning = kerning
      self.text_color = text_color
      self.font_name = font_name
      self.output_text_filename = output_text_filename
      
      self.videoname=videoname
      self.logo_filename=logo_filename
      
      self.fade_out_time=fade_out_time
      self.fade_in_time=fade_in_time
      self.time_between_videos=time_between_videos
      
      self.output_path = output_path
      self.output_fps=output_fps
      self.output_codec=output_codec #libx264 #mpeg4 #png
      self.output_video_width=output_video_width
      self.output_video_height=output_video_height
      self.video_bitrate=video_bitrate
      self.text_video_size = (self.output_video_width, self.output_video_height)
      self.output_video_name= "output_video.mp4" #self.videoname.split(".")[0]+"_"+str(random.randrange(10,10000))+".mp4"
      
      self.input_path = input_path
    
      self.txtClip = TextClip(self.phrase, color=self.text_color, font=self.font_name, kerning=self.kerning, fontsize=self.fontsize)
      self.cvc = CompositeVideoClip( [self.txtClip.set_pos('center')], size=self.text_video_size)
      self.rotMatrix = lambda a: np.array( [[np.cos(a),np.sin(a)], [-np.sin(a),np.cos(a)]])
      self.letters = findObjects(self.cvc)
    
    def vortex(self,screenpos,i,nletters):
        d = lambda t : 1.0/(0.3+t**8) #damping
        a = i*np.pi/ nletters # angle of the movement
        v = self.rotMatrix(a).dot([-1,0])
        if i%2 : v[1] = -v[1]
        return lambda t: screenpos+400*d(t)*self.rotMatrix(0.5*d(t)*a).dot(v)
      
    def moveLetters(self,letters,funcpos):
        return [ letter.set_pos(funcpos(letter.screenpos,i,len(letters)))
                  for i,letter in enumerate(letters)]
      
    def generate_text(self):
        # clips = [ CompositeVideoClip( self.moveLetters(self.letters,funcpos) , size = self.text_video_size ).subclip(0,5)
            #   for funcpos in [self.vortex]]
  
        # final_clip = concatenate_videoclips(clips)    
        # final_clip.write_videofile(self.output_path+self.output_text_filename, fps=self.output_fps, codec=self.output_codec, bitrate=self.video_bitrate, logger=None)
        self.cvc.duration = 4
        self.cvc.write_videofile(self.output_path+self.output_text_filename, fps=self.output_fps, codec=self.output_codec, bitrate=self.video_bitrate, logger=None)
        
    def generate_video(self):      
        self.generate_text()
        # videos
        video = VideoFileClip(self.input_path+self.videoname).resize(width=self.output_video_width)
        logo = VideoFileClip(self.logo_filename).resize(width=video.size[0])
        text = VideoFileClip(self.output_path+self.output_text_filename).resize(width=video.size[0])
        
        # audio fades
        logo = logo.audio_fadeout(self.fade_out_time)
        video = video.audio_fadein(self.fade_in_time).audio_fadeout(self.fade_out_time)
        
        # video fades
        logo = logo.fadeout(self.fade_out_time)
        text = text.fadein(self.fade_in_time).fadeout(self.fade_out_time)
        video = video.fadein(self.fade_in_time).fadeout(self.fade_out_time)
        
        # output video
        final = concatenate_videoclips([logo, text, video], padding=self.time_between_videos, method="compose")
        final.write_videofile(self.output_path+self.output_video_name, fps=self.output_fps, codec=self.output_codec, bitrate=self.video_bitrate, threads=4, audio=True, audio_fps=44100, logger=self.logger)
        return self.output_video_name