#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import random

LISSAGE= np.log2(10**-10)

#Algorithme étiquetant au hasard :-]  
def randchoice(cats,sentence):
	return [random.choice(list(cats)) for a in sentence]

#Algorithme d'étiquette de catégorie majoritaire :
#La fonction déduit l'étiquette majoritaire à partir du compte des catégories, et renvoie une fonction, majo,
#attribuant systématiquement l'étiquette majoritaire à tous les mots de la phrase.
def majoritywins(prevcounts):
	u=0
	for p in prevcounts:
		z=prevcounts[p]
		if z > u:
			u=z
			commonest=p
	
	def majo(sentence):
		return [commonest for a in sentence]
	
	print "Most common category :" + commonest
	return majo

#Cette fonction déduit une étiquette à partir de la meilleure probabilité contenue dans la matrice d'émission
#pour un mot. 
def baseline2(matrem, cats, sentence):
	if len(sentence) == 0:
		return []
	else:
		p,_=sentence[0]
		z= -np.Inf
		bestcat="N"
		
		for cat in cats:
			s=matrem.get((cat,p) ,LISSAGE)
			if s > z:
				z=s
				bestcat=cat
		return [bestcat] + baseline2(matrem, cats, sentence[1:])

#Cette fonction déduit la catégorie d'un mot à partir de la probabilité conjointe de son émission et de la transition depuis
#la catégorie précédente.
#Elle revient à choisir le chemin localement optimal dans le treillis de Viterbi, sans mémoire des états précédents
def naive(matran, matrem, cats, prev,sentence):
	if len(sentence) == 0:
		return []
	else:
		p,_=sentence[0]
		p=p.lower()
		z=-np.Inf
		bestcat="N"
	
		for cat in cats:
			s = matrem.get((cat,p), LISSAGE) + matran.get((prev,cat),LISSAGE)
			if s > z:
				z=s
				bestcat=cat
	
		return [bestcat] + naive(matran, matrem, cats, bestcat,sentence[1:])

#Algorithme de Viterbi
def viterbi(matran,matrem, cats,sentence):
	pointeurs = []
	viterbo = []

	previt = {}
	back1 = {}
	
	w,_=sentence[0]
	
	#Calcul de la meilleure probabilité pour le début de phrase = probabilité d'émission pour chaque catégorie + probabilité de transition
	#depuis un début de phrase
	for cat in cats:
		previt[cat] = matrem.get((cat,w),LISSAGE) + matran.get(("S",cat), LISSAGE)
		back1[cat] = "S"
	
	
	pointeurs.append(back1)
	for (w,_) in sentence[1:]:
		vitn = {}
		backn={}
		
		for cat in cats:
			bestprob = -np.Inf
			bestag = ""
			probem = matrem.get((cat,w),LISSAGE)
			
			for tag in cats:
				z= previt[tag] + probem + matran.get((tag,cat),LISSAGE)
				if z > bestprob:
					bestprob=z
					bestag=tag
			
			#Calcul de la meilleure probabilité pour chaque conjonction mot-étiquette-étiquette précédente
		
			vitn[cat] = bestprob
			backn[cat] = bestag
		
		pointeurs.append(backn)
		previt = vitn 
	
	bestprob = -np.Inf
	bestag = ""
	lastword=sentence[-1][0]
	
	#Calcul de la meilleure probabilité pour le dernier mot de la phrase.
	for tag in cats:
		z= previt[tag] + matran.get((tag,"S"),LISSAGE) #+ matrem.get((tag,lastword),LISSAGE)
		if z > bestprob:
			bestprob=z
			bestag=tag
	
	bestseq = ["S", bestag]
	
	cbt = bestag
	#Boucle qui va rechercher les étiquettes d'états précédents les plus probables, compte tenu de l'étiquette la plus probable déduite 
	#pour l'état final
	for bp in reversed(pointeurs):
		bestseq.append(bp[cbt])
		cbt=bp[cbt]
	
	bestseq.reverse()
	
	return bestseq[1:-1]
