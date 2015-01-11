#!/usr/bin/python 
# -*- coding: utf-8 -*-

import functools as funk
from collections import defaultdict

#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidY):
	score=0
	
	if len(poidY) == 0:
		score=len(traits)
	
	for t in traits:
		score += poidY[t]
	
	return score

def getfeatures(word):
	return set([word,"suff2_"+word[-2:],"suff3_" + word[-3:],"pref2_" +word[:2],"pref3_" + word[:3] ])

def classify(poids, traits):
	s=0.0
	tag="ERR"
	for x in poids:
		z=score(traits, poids[x])
		if z > s:
			s=z
			tag=x
	
	return tag


def perceptron(poids,sentence):
		tags=[]
		
		prevcat="S"
		prevword1="b1"
		prevword2="b2"
		for word,_ in sentence:
			traits=getfeatures(word)
			traits.update([prevcat,prevword1,prevword2])
	
			cat=classify(poids,traits)
			tags.append(cat)
			if prevword1:
				prevword2="2" + prevword1
				
			prevword1="prev_" + word
			prevcat=cat
		
	
		return tags

def perceptronmaker(cats,train):
	poids=defaultdict(lambda : defaultdict(float))
	accum=defaultdict(lambda : defaultdict(float))
	
	
	for cat in cats:
		poids[cat]
	
	for iterations in range(0, 2):
		print iterations
		for sentence in train:
			prevcat="S"
			prevword1="b1"
			prevword2="b2"
			for word,truecat in sentence:
				traits=getfeatures(word)
				traits.update([prevcat,prevword1,prevword2])
	
				cat=classify(poids,traits)
				prevword2="2" + prevword1
				prevword1="prev_" + word
				prevcat=cat
				
				if cat != truecat:
					for trait in traits:
						poids[truecat][trait] = poids[truecat][trait] + 1
						poids[cat][trait] = poids[cat][trait] - 1
			
	return poids
	
	
	
	
	
	
	
	
	
