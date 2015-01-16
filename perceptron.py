#!/usr/bin/python 
# -*- coding: utf-8 -*-

#Approche probabiliste du TAL - Arthur Lapraye - 2015

#Implémentation d'un perceptron

import random
import functools as funk
from collections import defaultdict

#Fonction retournant un score pour un jeu de traits donnés
def score(traits,poidY):
	return sum([poidY[t] for t in traits])
	
#Vu que les vecteurs de traits sont binaires, c'est plus logique de les représenter par des set() que par des dicts

#Fonction qui renvoie un vecteur de traits pour un mot donné, constitué du mot et de ses suffixes et préfixes
def getfeatures(word):
	a=set([word,"suff3_" + word[-3:] ,"pref3_" + word[:3], "suff2_"+word[-2:], "pref2_"+word[:2] ])
	if word[0] in u"ÄÖÜABCDEFGHIJKLMNOPQRSTUVWXYZ":
		a.update('_CAPITAL_')
	
	return a

#Fonction qui l'étiquette correspondant au meilleur score d'un vecteur de traits donné pour des vecteur de poids donné
def classify(poids, traits):
	return max(poids.keys(),key=lambda x : score(traits, poids[x]))

#def scores(poids,traits):
#	return sorted(poids.keys(),key=lambda x : score(traits, poids[x]))


#Fonction de catégorisation du perceptron
#Prend l'ensemble des vecteurs de poids en entrée, ainsi qu'une phrase
#Renvoie trois listes : la liste des meilleurs étiquettes, la liste des vecteurs de traits, 
#Et la liste des vraies catégories, pour l'entraînement du perceptron
def perceptron_t(poids,sentence):
		tags=[]
		traitsmots=[]
		truecats=[]
		
		lon=len(sentence)
		prevcat="S"
		prevword1="_begin_"
		prevtraits=set(prevword1)
		
		for  (pos,(word,truecat)) in enumerate(sentence):
			#Les traits utilisés comprennent pour chaque mot, sa forme, ses deux variétés de suffixe et de préfixe
			#Des traits "intrinsèques", indépendant de sa position.
			#Mais aussi des traits "contextuels", qui sont les traits intrinsèques de ses voisins
			#Si le voisin est un début de phrase, le seul trait contextuel est "_begin_"
			#Si le voisin est une fin de phrase, le seul trait contextuel est "_findephrase_"
			#La catégorie prédite pour le prédécesseur est aussi donnée, mais pas celle du successeur.  
			
			t1=getfeatures(word)
			#Récupération des traits intrinsèques
			
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

#Fonction utilisée pour le test du perceptron
#Utilise la fonction de catégorisation, mais ne garde que la liste de tags
#l'apprentissage  	
def perceptron(poids,sentence):
	return perceptron_t(poids,sentence)[0]

#Fonction d'apprentissage du perceptron
def perceptronmaker(cats,train,itermoi=10,poids=defaultdict(lambda : defaultdict(float))):
	
	for cat in cats:
		poids[cat]
	
	for iterations in range(0, itermoi):
		for sentence in train:
			#Pour chaque phrase du corpus d'apprentissage, les mots sont classifiés
			for (cat,truecat,traits) in zip(*perceptron_t(poids,sentence)):
				if cat != truecat:
					for trait in traits:
						#Mise à jour des poids en cas d'erreur
						poids[truecat][trait] = poids[truecat][trait] + 1
						poids[cat][trait] = poids[cat][trait] - 1
					
		print iterations+1
				
	return poids
	

