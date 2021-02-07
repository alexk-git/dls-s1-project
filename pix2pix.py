# импортируем необходимые биббиотеки
from PIL import Image
import sys

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.utils import save_image as save_image

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

device = 'cpu'

# Генератор
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        # Generator - UNet
        self.conv1_1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
        self.conv1_2 = nn.Conv2d(in_channels=16, out_channels=16, kernel_size=3, padding=1)
        self.conv2_1 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.conv2_2 = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1)
        self.conv3_1 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.conv3_2 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1)
        self.conv4_1 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.conv4_2 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1)

        self.conv5_1 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.conv5_2 = nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1)

        self.up6 = nn.Conv2d(in_channels=256, out_channels=128, kernel_size=3, padding=1)
        self.conv6_1 = nn.Conv2d(in_channels=256, out_channels=128, kernel_size=3, padding=1)
        self.conv6_2 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1)

        self.up7 = nn.Conv2d(in_channels=128, out_channels=64, kernel_size=3, padding=1)
        self.conv7_1 = nn.Conv2d(in_channels=128, out_channels=64, kernel_size=3, padding=1)
        self.conv7_2 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1)

        self.up8 = nn.Conv2d(in_channels=64, out_channels=32, kernel_size=3, padding=1)
        self.conv8_1 = nn.Conv2d(in_channels=64, out_channels=32, kernel_size=3, padding=1)
        self.conv8_2 = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1)

        self.up9 = nn.Conv2d(in_channels=32, out_channels=16, kernel_size=3, padding=1)
        self.conv9_1 = nn.Conv2d(in_channels=32, out_channels=16, kernel_size=3, padding=1)
        self.conv9_2 = nn.Conv2d(in_channels=16, out_channels=16, kernel_size=3, padding=1)
        self.conv9_3 = nn.Conv2d(in_channels=16, out_channels=3, kernel_size=3, padding=1)

    def forward(self, x):
        conv1 = nn.ReLU()(self.conv1_1(x))
        conv1 = nn.ReLU()(self.conv1_2(conv1))
        pool1 = nn.MaxPool2d(kernel_size=(2, 2))(conv1)
        conv2 = nn.ReLU()(self.conv2_1(pool1))
        conv2 = nn.ReLU()(self.conv2_2(conv2))
        pool2 = nn.MaxPool2d(kernel_size=(2, 2))(conv2)
        conv3 = nn.ReLU()(self.conv3_1(pool2))
        conv3 = nn.ReLU()(self.conv3_2(conv3))
        pool3 = nn.MaxPool2d(kernel_size=(2, 2))(conv3)
        conv4 = nn.ReLU()(self.conv4_1(pool3))
        conv4 = nn.ReLU()(self.conv4_2(conv4))
        drop4 = nn.Dropout2d(0.5)(conv4)
        pool4 = nn.MaxPool2d(kernel_size=(2, 2))(drop4)

        conv5 = nn.ReLU()(self.conv5_1(pool4))
        conv5 = nn.ReLU()(self.conv5_2(conv5))
        drop5 = nn.Dropout2d(0.5)(conv5)

        up6 = nn.Upsample(scale_factor=2, mode='nearest')(drop5)
        up6 = nn.ReLU()(self.up6(up6))
        merge6 = torch.cat([drop4, up6], dim=1)
        conv6 = nn.ReLU()(self.conv6_1(merge6))
        conv6 = nn.ReLU()(self.conv6_2(conv6))

        up7 = nn.Upsample(scale_factor=2, mode='nearest')(conv6)
        up7 = nn.ReLU()(self.up7(up7))
        merge7 = torch.cat([conv3, up7], dim=1)
        conv7 = nn.ReLU()(self.conv7_1(merge7))
        conv7 = nn.ReLU()(self.conv7_2(conv7))

        up8 = nn.Upsample(scale_factor=2, mode='nearest')(conv7)
        up8 = nn.ReLU()(self.up8(up8))
        merge8 = torch.cat([conv2, up8], dim=1)
        conv8 = nn.ReLU()(self.conv8_1(merge8))
        conv8 = nn.ReLU()(self.conv8_2(conv8))

        up9 = nn.Upsample(scale_factor=2, mode='nearest')(conv8)
        up9 = nn.ReLU()(self.up9(up9))
        merge9 = torch.cat([conv1, up9], dim=1)
        conv9 = nn.ReLU()(self.conv9_1(merge9))
        conv9 = nn.ReLU()(self.conv9_2(conv9))
        conv9 = nn.Tanh()(self.conv9_3(conv9))

        return conv9


transformation = transforms.Compose(
    [transforms.Resize((256, 256)),
     transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

# Создадим модель из загруженных весов
sketches_model = Generator().to('cpu')
sketches_model.load_state_dict(torch.load("gdrive/MyDrive/pix2pix/pytorch_models/pix2pix_generator_sketches_e{}.pt".format(1000)))
sketches_model.eval()

# Загрузим оригинал и проведём с ним необходимые преобразования
#image = Image.open('original.jpg')
image = Image.open(sys.argv[1])
v, h = image.size
image = transformation(image)
image = image[None, :, :]

# инференс
result_image = sketches_model(image)
result_image = result_image.to("cpu").detach()

# созраним результат
result_image = transforms.Grayscale()(result_image)
save_image(transforms.Resize((h, v))(result_image), "output.jpg")

