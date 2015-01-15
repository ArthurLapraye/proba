#!/usr/bin/python 
# -*- coding: utf-8 -*-

#Approche probabiliste du TAL - Arthur Lapraye - 2015

#Implémentation d'un perceptron

import random
import functools as funk
from collections import defaultdict

#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts
def score(traits,poidY):
	return sum([poidY[t] for t in traits])

def getfeatures(word):
	a=set([word,"suff3_" + word[-3:] ,"pref3_" + word[:3], "suff2_"+word[-2:], "pref2_"+word[:2] ])
	if word[0] in u"ÄÖÜABCDEFGHIJKLMNOPQRSTUVWXYZ":
		a.update('_CAPITAL_')
	
	return a

def classify(poids, traits):
	return max(poids.keys(),key=lambda x : score(traits, poids[x]))

#def scores(poids,traits):
#	return sorted(poids.keys(),key=lambda x : score(traits, poids[x]))


def perceptron_t(poids,sentence):
		tags=[]
		traitsmots=[]
		truecats=[]
		
		lon=len(sentence)
		prevcat="S"
		prevword1="_begin_"
		prevtraits=set(prevword1)
		
		for  (pos,(word,truecat)) in enumerate(sentence):
			t1=getfeatures(word)
			
			traits=set([prevcat])
			traits.update(prevtraits)
			traits.update(t1)
			
			prevtraits=set([ "prev_"+trait for trait in t1])
			
			if pos == lon-1:
				traits.update("_Findephrase_")
			else:
				traits.update(["next_"+p for p in getfeatures(sentence[pos+1][0])])
	
			cat=classify(poids,traits)
			tags.append(cat)
			truecats.append(truecat)
			traitsmots.append(traits)
				
			prevcat="prev_"+cat
		
	
		return (tags,truecats,traitsmots)
	
def perceptron(poids,sentence):
	return perceptron_t(poids,sentence)[0]

def perceptronmaker(cats,train,itermoi=10,poids=defaultdict(lambda : defaultdict(float))):
	update=defaultdict(lambda : defaultdict(float))
	
	for cat in cats:
		poids[cat]
	
	for iterations in range(0, itermoi):
		for sentence in train:
			for (cat,truecat,traits) in zip(*perceptron_t(poids,sentence)):
				if cat != truecat:
					for trait in traits:
						poids[truecat][trait] = poids[truecat][trait] + 1
						poids[cat][trait] = poids[cat][trait] - 1
					
		print iterations+1
				
	return poids
	
	
