"""
Train non-autoregressive spectrogram inversion model on the german single speaker dataset by Hokuspokus
"""

import os
import random
import warnings

import torch

from MelGAN.MelGANDataset import MelGANDataset
from MelGAN.MelGANGenerator import MelGANGenerator
from MelGAN.MelGANMultiScaleDiscriminator import MelGANMultiScaleDiscriminator
from MelGAN.melgan_train_loop import train_loop

warnings.filterwarnings("ignore")

torch.manual_seed(13)
random.seed(13)


def build_path_to_transcript_dict():
    path_train = "/mount/resources/speech/corpora/LibriTTS/train-clean-100"
    path_valid = "/mount/resources/speech/corpora/LibriTTS/dev-clean"

    path_to_transcript = dict()
    # we split training and validation differently, so we merge both folders into a single dict
    for speaker in os.listdir(path_train):
        for chapter in os.listdir(os.path.join(path_train, speaker)):
            for file in os.listdir(os.path.join(path_train, speaker, chapter)):
                if file.endswith("normalized.txt"):
                    with open(os.path.join(path_train, speaker, chapter, file), 'r',
                              encoding='utf8') as tf:
                        transcript = tf.read()
                    wav_file = file.split(".")[0] + ".wav"
                    path_to_transcript[os.path.join(path_train, speaker, chapter, wav_file)] = transcript
    for speaker in os.listdir(path_valid):
        for chapter in os.listdir(os.path.join(path_valid, speaker)):
            for file in os.listdir(os.path.join(path_valid, speaker, chapter)):
                if file.endswith("normalized.txt"):
                    with open(os.path.join(path_valid, speaker, chapter, file), 'r',
                              encoding='utf8') as tf:
                        transcript = tf.read()
                    wav_file = file.split(".")[0] + ".wav"
                    path_to_transcript[os.path.join(path_valid, speaker, chapter, wav_file)] = transcript
    return path_to_transcript


def get_file_list():
    return list(build_path_to_transcript_dict().keys())


if __name__ == '__main__':
    print("Preparing")
    fl = get_file_list()
    model_save_dir = "Models/MelGAN/MultiSpeaker/LibriTTS"
    device = torch.device("cuda:2")
    train_dataset = MelGANDataset(list_of_paths=fl[:-100])
    valid_dataset = MelGANDataset(list_of_paths=fl[-100:])
    generator = MelGANGenerator()
    generator.reset_parameters()
    multi_scale_discriminator = MelGANMultiScaleDiscriminator()
    if not os.path.exists(model_save_dir):
        os.makedirs(model_save_dir)
    print("Training model")
    train_loop(batchsize=32,
               epochs=600000,  # just kill the process at some point
               generator=generator,
               discriminator=multi_scale_discriminator,
               train_dataset=train_dataset,
               valid_dataset=valid_dataset,
               device=device,
               generator_warmup_steps=400000,
               model_save_dir=model_save_dir)