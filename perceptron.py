#!/usr/bin/python 


#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidY):
	score=0;
	
	if len(poidY) > 0:
		score=len(traits)
	
	for t in traits:
		score += poidY[t]
	
	return score
	
def train(mots):
	pCat="s"

def classify(poids, traits):
	return max(poids,lambda x : score(traits, x))

def perceptronmaker(cats,train):
	poids=defaultdict(lambda : defaultdict(float))
	accum=defaultdict(lambda : defaultdict(float))
	
	for cat in cats:
		poids[cat]
	
	for (word,truecat) in train: 
		traits=set([word,word[-2:],word[-3:],word[:2],word[:3]])
		traits.update([prevcat,prevsuffix])
		
		cat=classify(poids,traits)
	
	
	
	
	
	
	
	
