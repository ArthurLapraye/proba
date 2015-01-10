#!/usr/bin/python 


def argmax(f, Y):
	return max(Y,key=f)
	
#for epoch in range(1, K):
#	for 

#traits= set()

#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidsY):
	score=0;
	for t in traits:
		score += poidsY[t]
	
	return score


def classify(poids, traits):
	
	
def train(mots):
	pCat="s"
	
