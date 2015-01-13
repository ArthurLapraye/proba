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
	a=set([word,"suff3_" + word[-3:],"pref3_" + word[:3] ])
	if word[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
		a.update('_CAPITAL_')
	
	return a

def classify(poids, traits):
	return max(poids.keys(),key=lambda x : score(traits, poids[x]))


def perceptron(poids,sentence):
		tags=[]
		
		prevcat="S"
		prevword1="_begin_"
		#prevword2="b2"
		lon=len(sentence)
		prevtraits=set()
		for  (pos,(word,_)) in enumerate(sentence):
			t1=getfeatures(word)
			
			traits=set([prevcat,prevword1])
			traits.update(prevtraits)
			traits.update(t1)
			
			prevtraits=set([ "prev_"+trait for trait in t1])
			
			if pos == lon-1:
				traits.update("_Findephrase_")
			else:
				traits.update(["next_"+p for p in getfeatures(sentence[pos+1][0])])
	
			cat=classify(poids,traits)
			tags.append(cat)
				
			#prevword1="prev_" + word
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
			prevword1="_begin_"
			lon=len(sentence)
			prevtraits=set()
			for  (pos,(word,truecat)) in enumerate(sentence):
				
				t1=getfeatures(word)
				
				traits=set([prevcat,prevword1])
				traits.update(prevtraits)
				traits.update(t1)
				
				prevtraits=set([ "prev_"+trait for trait in t1])
				
				if pos == lon-1:
					traits.update("_Findephrase_")
				else:
					#traits.update("nextword_"+sentence[pos+1][0])
					traits.update(["next_"+p for p in getfeatures(sentence[pos+1][0])])
	
				cat=classify(poids,traits)
				#prevword2="2" + prevword1
				#prevword1="prev_" + word
				prevcat=cat
				
				if cat != truecat:
					for trait in traits:
						poids[truecat][trait] = poids[truecat][trait] + 1
						poids[cat][trait] = poids[cat][trait] - 1
	
				
	return poids
	
	
	
	
	
	
	
	
	
