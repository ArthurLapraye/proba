#!/usr/bin/python 
# -*- coding: utf-8 -*-

#Implémentation de l'algorithme de Viterbi - TP3 - Arthur Lapraye - 2014

import re
import sys
import random
import numpy as np
import functools as funk
from optparse import OptionParser
from viterbi import *
import perceptron as pers

usage=u"""
	./Lapraye-tp3.py [options] corpus
	  Ce programme implémente l'algorithme de Viterbi pour l'étiquetage morpho-syntaxique, 
	  ainsi que d'autres algorithmes plus simplistes afin d'en comparer les performances. 
	  Il opère sur un corpus dont 90% est utilisé pour la création de matrices de transitions
	  et d'émission, et 10% est utilisé pour tester les algorithmes. 
	  """

p = OptionParser(usage=usage)


p.add_option("-m", "--map", action="store", dest="mappingfile",default=None, 
	help=u"Option pour offrir un fichier de mapping d'un jeu de tags aux tags universels")


p.add_option("-c", "--confusion",
                  action="store_true", dest="matrice", default=False,
                  help=u"Cette option permet d'afficher les matrices de confusions pour chaque algorithme et de les comparer de façon plus fine.")

p.add_option("-a", "--absolute-values",
                  action="store_false", dest="percent", default=True,
                  help=u"Cette option permet de remplacer les pourcentages affichés par défaut par des valeurs absolues.")
                  
(op,args)=p.parse_args()

#Variables globales
TEST=9 
MAPPINGFILE=op.mappingfile
MATRICE=op.matrice
PERCENT=op.percent
LISSAGE= np.log2(10**-10)

def mapit(tagmapfile):
	tabz=re.compile("[\t\n]")
	mapping={}
	with open(tagmapfile) as tagmap:
		for line in tagmap:
			[ant,img,_]=tabz.split(line)
			mapping[ant] = img
	
	return mapping
			


def liredonnees(filename,mapping=None):
	tabz=re.compile("\t") #Expression régulière pour couper les lignes du fichier
	test=[] #Corpus de test
	train=[] #corpus d'entraînement pour le perceptron
	sentence=[] #Liste de tuples mots/catégorie utilisée pour construire le corpus de test
	wordcounts = {} #comptage de mots 
	prevcounts = {} #comptage de catégories
	prevcounts = {} #comptage de catégories
	matrem = {} #distribution d'émission
	matran = {} #distribution de transition
	
	cats=set() #Ensemble des catégories
	
	prevcat = "S"	#Séparateur de phrases
	
	c=random.randint(0,TEST)
	
	with open(filename) as fichier:
		for line in fichier:
			if line != '\n':
				[a,word,lemm,_,cat, f,g,h,i,j ,k,l,m,n,o]=tabz.split(line)
				
				if mapping:
					cat=mapping[cat]
				
				cats.add(cat)
				
				#[phranum,wordnum]=num.split(a)
				
				if c == TEST: 
					sentence.append((word, cat))
				else: 
					prevcounts[prevcat] = prevcounts.get(cat,0.0) + 1
					wordcounts[word] = wordcounts.get(word,0.0) + 1
					matrem[cat,word] = matrem.get((cat,word), 0.0) +1
					matran[prevcat,cat] = matran.get( (prevcat, cat), 0.0) + 1
					prevcat = cat
					
				
			else:
				if c == TEST:
					test.append(sentence)
					
				else:
					matran[cat,"S"] = matran.get( (cat,"S"), 0.0) + 1
					prevcat = "S"
					train.append(sentence)
				
				sentence=[]
				c = random.randint(0,TEST)
					
					
	for c in matran:
		p,q=c
		matran[c]=np.log2(matran[c]/prevcounts[p])

	for c in matrem:
		p,q=c
		matrem[c]=np.log2(matrem[c]/prevcounts[p])
	
	return (train,test,matran,matrem,prevcounts,wordcounts,cats)
		
#Fonction testant les algorithmes d'étiquetage sur le corpus de test.
def testit(z):
	wc = 0.0	
	nice = 0.0
	errs = 0.0
	
	realcats = dict(zip(list(cats),(0 for a in list(cats))))
	
	matcon={}
	
	for ca1 in cats: 
		for ca2 in cats:
			matcon[ca1,ca2]=0
	
	for t in test:
		for w in zip(z(t),t):
			wc += 1.0
			truecat=w[1][1]
			realcats[truecat] += 1
			matcon[truecat,w[0]] += 1
			
			if w[0] == truecat:
				nice += 1.0
			else:
				errs += 1.0
		
	
	if MATRICE:
		#Les étiquettes de catégories réelles sont affichées à gauches
		#Les étiquettes prédites par l'algorithme sont affichées en haut
		#Il me semble que c'est conventionnel.
		
		print "Matrice de confusion :"
		z=list(cats)
		print "\t" +"\t".join(z)
		for ca in cats:
			if realcats[ca] != 0.0:
				if PERCENT:
					p=[str((100*matcon[ca,a])/realcats[ca])+"%" for a in z]
				else:
					p=[str(matcon[ca,a]) for a in z]
					
				print ca + "\t" + "\t".join(p)
	
	precision= str(100*nice/wc)+"%" if PERCENT else str(nice) + "/" + str(wc)
	print "Précision globale : " + precision  + "\n"

#Programme :
if len(args) < 1:
	print "Erreur : aucun corpus spécifié"
	sys.exit(1)


if MAPPINGFILE:
	m=mapit(MAPPINGFILE)
else:
	m=None

(train,test,matran,matrem,prevcounts,wordcounts,cats)=liredonnees(args[0],mapping=m)

ALL=False

if ALL:
	print "Sélection de la catégorie au hasard : "
	testit(funk.partial(randchoice,cats)) 
	print "Sélection de la catégorie la plus courante : " 
	testit(majoritywins(prevcounts))
	print "Sélection basée sur la catégorie la plus probable de la forme" 
	testit(funk.partial(baseline2,matrem,cats))

print "Sélection basée sur le chemin localement optimal :"
testit(funk.partial(naive,matran, matrem, cats, "S"))
print "Sélection basée sur le chemin optimal déduit par l'algorithme de Viterbi :" 
testit(funk.partial(viterbi,matran,matrem,cats))
print "Perceptron"
testit(pers.perceptronmaker(cats,train))

#Les derniers algorithmes montrent des précisions globales assez proches, 
#C'est en regardant dans les matrices de confusion qu'on voit que Viterbi est meilleur, 
#en particulier pour distinguer les clitiques et les déterminants.
#On note que les catégories sont parfois douteuse : e.g. la catégorie ET contient les mots étrangers
#Quels que soient leur contextes d'apparition. Elle mélange des mots qui appartiennent à des parties du discours différentes.
#Quand Viterbi classe 36% d'entre eux parmi les noms, j'ai plus envie de le croire lui que de croire le corpus. 

#Notons aussi que le fichier ftb2.txt fait apparaître une catégorie "Dmp" 
#Elle n'apparaît que pour le nombre trois_cent_mille, et résulte d'une erreur de formatage. 
#La ligne dit 
#trois_cent_mille	trois_cent_mille	Dmp	NA	NA	NA	NA	NA	NA
#Alors que ça devrait probablement être
#trois_cent_mille	trois_cent_mille	D	NA	m	p	NA	NA	NA


