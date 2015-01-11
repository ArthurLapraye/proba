#!/usr/bin/python 
# -*- coding: utf-8 -*-

from collections import defaultdict

#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidY):
	score=0;
	
	if len(poidY) > 0:
		score=len(traits)
	
	for t in traits:
		score += poidY[t]
	
	return score

def getfeatures(word):
	print word
	return set([word,"suff2_"+word[-2:],"suff3_" + word[-3:],"pref2_" +word[:2],"pref3_" + word[:3] ])

def classify(poids, traits):
	return max(poids,key=lambda x : score(traits, x))

def perceptronmaker(cats,train):

	prevword1=None
	prevword2=None
	prevcat="S"
	poids=defaultdict(lambda : defaultdict(float))
	accum=defaultdict(lambda : defaultdict(float))
	
	for cat in cats:
		poids[cat]
	
	
	#prevsuffix=None
	
	for _ in range(0, 100):
		for sentence in train:
			for (word,truecat) in sentence: 
				traits=getfeatures(word)
				traits.update([prevcat,prevword1,prevword2])
				traits.remove(None)
		
				cat=classify(poids,traits)
		
				if cat != truecat:
					for trait in traits:
						poids[truecat][trait] += 1
						poids[cat][trait] -= 1
				
				prevcat="prev_" + cat
				if prevword1:
					prevword2="2" + prevword1
				
				prevword1="prev_" + word
			
			prevcat="S"
			prevword1=None
			prevowrd2=None
	
	def perceptron(sentence):
		for word,_ in sentence:
			traits=getfeatures(word)
			traits.update([prevcat,prevword1,prevword2])
			traits.remove(None)
	
			cat=classify(poids,traits)
			tags.append(cat)
			if prevword1:
				prevword2="2" + prevword1
				
			prevword1="prev_" + word
			prevcat=cat
	
		prevcat="S"
		prevword1=None
		prevword2=None
		return tags
	
	
	return perceptron
	
	
	
	
	
	
	
	
	
