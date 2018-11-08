# pylint: disable=E0401, E0302
import torch
from torch import nn

class CVAE(nn.Module):
    def __init__(self, latent_size, num_labels=1):
        super(CVAE, self).__init__()

        self.latent_size = latent_size
        self.num_labels = num_labels
        
        self.encoder = Encoder(latent_size, num_labels)
        self.decoder = Decoder(latent_size, num_labels)

    def reparameterization(self, mean, log_var):
        return 0
    # def re_param(self, mu, log_var):
		# #do the re-parameterising here
		# sigma = torch.exp(log_var/2)  #sigma = exp(log_var/2) #torch.exp(log_var/2)
		# if self.useCUDA:
		# 	eps = Variable(torch.randn(sigma.size(0), self.nz).cuda())
		# else: eps = Variable(torch.randn(sigma.size(0), self.nz))
		
		# return mu + sigma * eps  #eps.mul(simga)._add(mu)

    def forward(self, x):
        mean, log_var, y = self.encoder(x)
        z = self.reparameterization(mean, log_var)
        rec = self.decoder(y, z)

        return rec, mean, log_var, y

    def loss(self, rec_x, x, mean, log_var):
        return 0
    # def loss(self, rec_x, x, mu, logVar):
	# 	sigma2 = Variable(torch.Tensor([self.sig]))
	# 	if self.useCUDA:
	# 		sigma2 = sigma2.cuda()
	# 	logVar2 = torch.log(sigma2)
	# 	#Total loss is BCE(x, rec_x) + KL
	# 	BCE = F.binary_cross_entropy(rec_x, x, size_average=False)  #not averaged over mini-batch if size_average=FALSE and is averaged if =True 
	# 	#(might be able to use nn.NLLLoss2d())
	# 	if self.sig == 1:
	# 		KL = 0.5 * torch.sum(mu ** 2 + torch.exp(logVar) - 1. - logVar) #0.5 * sum(1 + log(var) - mu^2 - var)
	# 	else:
	# 		KL = 0.5 * torch.sum(logVar2 - logVar + torch.exp(logVar) + (mu ** 2 / 2 * sigma2 ** 2) - 0.5)
	# 	return BCE / (x.size(2) ** 2),  KL / mu.size(1)

class Encoder(nn.Module):
    def __init__(self, latent_size, num_labels):
        super(Encoder, self).__init__()
        # (3 * 64 * 64)
        self.encoder1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2),
            nn.ReLU()
        )
        # (32 * 32 * 32)
        self.encoder2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=2, padding=2),
            nn.ReLU()
        )
        # (64 * 16 * 16)
        self.encoder3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=5, stride=2, padding=2),
            nn.ReLU()
        )
        # (128 * 8 * 8)
        self.encoder4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=5, stride=2, padding=2),
            nn.ReLU()
        )
        # (256 * 4 * 4)
        self.mean = nn.Linear(256*4*4, latent_size)
        self.log_var = nn.Linear(256*4*4, latent_size)
        self.y = nn.Sequential(
            nn.Linear(256*4*4, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        x = self.encoder1(x)
        x = self.encoder2(x)
        x = self.encoder3(x)
        x = self.encoder4(x)
        x = x.view(x.size(0), -1)
        mean = self.mean(x)
        log_var = self.log_var(x)
        y = self.y(x.detach())

        return mean, log_var, y

class Decoder(nn.Module):
    def __init__(self, latent_size, num_labels):
        super(Decoder, self).__init__()

        self.decoder1 = nn.Sequential(
            nn.Linear(latent_size+1, 256*4*4),
            nn.ReLU()
        )
        self.decoder2 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=3, stride=2, padding=1 ,output_padding=1),
		    nn.BatchNorm2d(128)
        )
        self.decoder3 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1 ,output_padding=1),
		    nn.BatchNorm2d(128)
        )
        self.decoder4 = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1 ,output_padding=1),
		    nn.BatchNorm2d(32)
        )
        self.decoder5 = nn.Sequential(
            nn.ConvTranspose2d(32, 3, kernel_size=3, stride=2, padding=1 ,output_padding=1),
		    nn.Sigmoid()
        )
    
    def forward(self, y, z):
        x = torch.cat([y, z], dim=1)
        x = self.decoder1(x)
        x = x.view(z.size(0), -1, 4, 4)
        x = self.decoder2(x)
        x = self.decoder3(x)
        x = self.decoder4(x)
        x = self.decoder5(x)

        return x
