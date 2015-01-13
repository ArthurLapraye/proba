#!/usr/bin/python 
# -*- coding: utf-8 -*-

import random
import functools as funk
from collections import defaultdict

#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidY):
	return sum([poidY[t] for t in traits])

def getfeatures(word):
	return set([word,"suff2_"+word[-2:],"pref2_" +word[:2] ]) #"suff3_" + word[-3:],"pref3_" + word[:3] ])

def classify(poids, traits):
	return max(poids.keys(),key=lambda x : score(traits, poids[x]))


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

def perceptronmaker(cats,train,itermoi=10,averaged=False):
	poids=defaultdict(lambda : defaultdict(float))
	accum=defaultdict(lambda : defaultdict(float))
	i=0.0
	
	for cat in cats:
		poids[cat]
	
	for iterations in range(0, itermoi):
		print iterations
		for sentence in train:
			prevcat="S"
			prevword1="b1"
			#prevword2="b2"
			for word,truecat in sentence:
				traits=getfeatures(word)
				traits.update([prevcat,prevword1,'canard'])
	
				cat=classify(poids,traits)
				#prevword2="2" + prevword1
				prevword1="prev_" + word
				prevcat=cat
				
				if cat != truecat:
					for trait in traits:
						poids[truecat][trait] = poids[truecat][trait] + 1
						poids[cat][trait] = poids[cat][trait] - 1
				
				i += 1
				
				if averaged:
					for cat in poids:
						for w in poids[cat]:
							accum[cat][w] += poids[cat][w]
				
	if averaged:
		for cat in poids:
			for w in poids[cat]:
				accum[cat][w] /= i
			
		return accum
	else:
		return poids
	
	
	
	
	
	
	
	
	
