#!/usr/bin/python 
# -*- coding: utf-8 -*-

#Projet Approche Probabiliste du TAL - Arthur Lapraye - 2015

import re
import sys
import math
import random
import numpy as np
import functools as funk
from optparse import OptionParser
from viterbi import *
from perceptron import *

usage=u"""
	Usage:
	./etiquetage-test.py [options] corpus
	  Ce programme implémente l'algorithme de Viterbi et l'algorithme du perceptron
	  pour l'étiquetage morpho-syntaxique,ainsi que d'autres algorithmes plus simplistes afin d'en comparer les performances. 
	  
	  Il opère sur un corpus dont 90% des phrases est utilisé 
	  pour l'entraînement et 10% est utilisé pour tester les algorithmes,
	  la répartition étant faite au hasard.
	  
	  -h --help pour l'aide.
	  """

#Paramètres du script
p = OptionParser(usage=usage)

p.add_option("-i","--iteration", action="store",dest="iteration", default=20,help=u"Nombres d'itérations du perceptron")

p.add_option("-m", "--map", action="store", dest="mappingfile",default=None, 
	help=u"Option prenant en paramètre un fichier de mapping d'un jeu de tags aux tags universels")


p.add_option("-c", "--confusion",
                  action="store_true", dest="matrice", default=False,
                  help=u"Cette option permet d'afficher les matrices de confusions pour chaque algorithme et de les comparer de façon plus fine.")

p.add_option("-l","--latex",action="store_true",dest="latex",default=False, help=u"Option pour spécifier l'affichage des matrices de confusion selon la syntaxe LaTeX. N'a pas d'effet si utilisé sans -c ou --confusion")


p.add_option("-a", "--absolute-values",
                  action="store_false", dest="percent", default=True,
                  help=u"Cette option permet de remplacer les pourcentages affichés par défaut par des valeurs absolues.")
                  
(op,args)=p.parse_args()

#Variables globales
TEST=9 
MAPPINGFILE=op.mappingfile
MATRICE=op.matrice
PERCENT=op.percent
ITERATIONS=int(op.iteration)
LATEX=op.latex

if LATEX:
	sep=" & "
	endline="\\\\"
	percentsign="\%"
else:
	percentsign="%"
	sep="\t"
	endline=" "

#Fonction de mapping de tags
#Prend en entrée un fichier .map, renvoie un dictionnaire permettant de retrouver le tag universel correspondant 
#au tag riche donné en clef
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
	
	c=random.randint(0,TEST) # Tirage au sort pour l'assignation d'une phrase au corpus d'entraînement ou de test
	
	with open(filename) as fichier:
		for line in fichier:
			if line != '\n':
				[a,word,lemm,_,cat, f,g,h,i,j ,k,l,m,n,o]=tabz.split(line.decode("UTF-8"))
				
				if mapping:
					cat=mapping[cat]
				
				cats.add(cat)
				
				#[phranum,wordnum]=num.split(a)
				
				sentence.append((word, cat))
				
				if c != TEST: 
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
#Et affichant optionnellement la matrice de confusion des algorithmes
#Elle prend une fonction d'étiquetage en entrée, l'applique à la phrase
#Et crée ensuite la matrice de confusion
def testit(z,M=MATRICE):
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
		
	
	if M:
		
		#Les étiquettes de catégories réelles sont affichées à gauches
		#Les étiquettes prédites par l'algorithme sont affichées en haut
		#Il me semble que c'est conventionnel.
		print "Matrice de confusion :"
		z=list(cats)
		print sep +sep.join(z) + endline
		for ca in cats:
			if realcats[ca] != 0.0:
				if PERCENT:
					p=[str((100*matcon[ca,a])/realcats[ca])+percentsign for a in z]
				else:
					p=[str(matcon[ca,a]) for a in z]
					
				print ca + sep + sep.join(p) + endline
	
	p=nice/wc
	precision= str(100*p)+"%" if PERCENT else str(nice) + "/" + str(wc)
	print u"Précision globale : " + precision  + "\n"
	return p


#Fonctions de calcul de distance des vecteurs.
def manhattan(w1,w2):
	return sum([ abs(w1[k]-w2[k]) for k in w1])

def euclide(w1,w2):
	return math.sqrt(sum([ (w1[k]-w2[k])**2 for k in w1]))
	
def distinfini(w1,w2):
	return max([ abs(w1[k]-w2[k]) for k in w1])

#Programme :
if len(args) < 1:
	print u"ERREUR : aucun corpus spécifié"
	print ""
	print usage
	sys.exit(1)


if MAPPINGFILE:
	m=mapit(MAPPINGFILE)
else:
	m=None

(train,test,matran,matrem,prevcounts,wordcounts,cats)=liredonnees(args[0],mapping=m)

ALL=False #Changer à True pour montrer les algorithmes qui sont sous la baseline retenue

if ALL:
	print u"Sélection de la catégorie au hasard : "
	testit(funk.partial(randchoice,cats)) 
	print u"Sélection de la catégorie la plus courante : " 
	testit(majoritywins(prevcounts))
	
	print u"Sélection basée sur le chemin localement optimal :"
	testit(funk.partial(naive,matran, matrem, cats, "S"))

#Baseline
print u"Sélection basée sur la catégorie la plus probable de la forme" 
testit(funk.partial(baseline2,matrem,cats))
print u"Sélection basée sur le chemin optimal déduit par l'algorithme de Viterbi :" 
testit(funk.partial(viterbi,matran,matrem,cats))


print "Perceptron",ITERATIONS
weight=perceptronmaker(cats,train,ITERATIONS)
z=testit(funk.partial(perceptron,weight))

print "Taille du corpus d'entraînement :",len(train), "Taille du corpus de test : ", len(test)
print "Nombre de tags :",len(weight)
#print [len(weight[x]) for x in weight]

#Ceci permet d'afficher les traits les plus informatifs et les moins informatifs.
#L'utilisation de la valeur absolue permet de dégager aussi bien les traits prédicteurs que les traits
#antiprédicteurs d'une catégorie donnée.
#C'est désactivé parce que ça prend beaucoup de place dans le terminal.
if False:
	for z in weight:
		feats=(sorted(weight[z],key=lambda x : abs(weight[z][x]),reverse=True))
		print "Meilleur traits pour "+z	
		print "\n\t".join([ x+" : "+str(weight[z][x]) for x in feats[:10] ])
		print "Pire traits pour " + z
		print "\n\t".join([ x+" : "+str(weight[z][x]) for x in feats[-10:] ])
	
		#print "\t",x,weight[z][x]

#Affichage des matrices de distances entre vecteurs 
for (funcname,func) in [("Manhattan",manhattan),("Euclide",euclide),(u"«Infini»",distinfini)]:
	print "Distance utilisée :",funcname
	if MATRICE:
		print sep+sep.join(weight.keys())+endline
	mini=0
	(min1,min2)=(None,None)
	for z in weight:
		dists=[]
		
		for y in weight:
			p=func(weight[z],weight[y])
			dists.append(p)
			if z != y and (p < mini or mini==0):
				mini=p
				(min1,min2)=(z,y)
		if MATRICE:	
			print z+sep+sep.join([str(int(x)) for x in dists])+" "+endline
	print "Vecteurs les plus proches :",min1,min2
	


