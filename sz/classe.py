# -*- coding: utf-8 -*-
"""
/***************************************************************************
 model
                                 A QGIS plugin
 Landslide Susceptibility Zoning
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-06-22
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Giacomo Titti
        email                : giacomotitti@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import numpy as np
from osgeo import gdal,osr
import sys
import math
import csv
from qgis.core import QgsMessageLog,QgsRasterLayer
import processing
import os
import ogr
from qgis import *
from qgis.analysis import *

class WoE:
    def iter(self):
        listcause=[]
        listclasses=[]
        if self.Wcause1==None:
            pass
        else:
            listcause.append(self.Wcause1)
            listclasses.append(self.classes1)
        if self.Wcause2==None:
            pass
        else:
            listcause.append(self.Wcause2)
            listclasses.append(self.classes2)
        if self.Wcause3==None:
            pass
        else:
            listcause.append(self.Wcause3)
            listclasses.append(self.classes3)
        if self.Wcause4==None:
            pass
        else:
            listcause.append(self.Wcause4)
            listclasses.append(self.classes4)
        for y in range(self.ii):
            if self.Wcauselista[y]==None:
                pass
            else:
                listcause.append(self.Wcauselista[y])
                listclasses.append(self.classeslista[y])
        #######################################################################
        countcause=len(listcause)######delete empty cause!!!!!!!!!!
        #print(listclasses)
        #print(listcause)
        if countcause==0:#verify empty row input
            QgsMessageLog.logMessage('Select at least one cause', tag="WoE")
            raise ValueError  # Select at least one cause, see 'WoE' Log Messages Panel
        ####################################translate dem and inventory
        self.newXNumPxl=(np.ceil(abs(self.xmax-self.xmin)/(self.w))-1).astype(int)
        self.newYNumPxl=(np.ceil(abs(self.ymax-self.ymin)/(self.h))-1).astype(int)
        self.xsize=self.newXNumPxl
        self.ysize=self.newYNumPxl
        self.shape=np.array([self.newXNumPxl,self.newYNumPxl])
        self.extent = "%s,%s,%s,%s" % (self.xmin, self.xmax, self.ymin, self.ymax)
        ##############
        self.origine=[self.xmin,self.ymax]
        #######################################inventory from shp to tif
        #try:

        #try:
        dem_datas=np.zeros((self.ysize,self.xsize),dtype='int64')
        # write the data to output file
        rf1='/tmp/01inv.tif'
        dem_datas1=np.zeros(np.shape(dem_datas),dtype='float32')
        dem_datas1[:]=dem_datas[:]#[::-1]
        w1=self.w
        h1=self.h*(-1)
        self.array2raster(rf1,w1,h1,dem_datas1,self.origine)##########rasterize inventory
        del dem_datas
        del dem_datas1
        ##################################
        self.IN3a=rf1
        self.IN2a='/tmp/02invq.tif'
        #IN2b='/tmp/03invq.tif'
        #self.IN3a='/tmp/04inventorynxn.tif'
        #self.cutextent(IN1a,IN2a)
        self.cut(self.IN3a,self.IN2a)##########traslate inventory
        if self.polynum==0:
            self.IN2a=self.IN3a
        self.ds15= None
        self.ds15 = gdal.Open(self.IN2a)
        if self.ds15 is None:#####################verify empty row input
            QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
            raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
        ap=self.ds15.GetRasterBand(1)
        NoData=ap.GetNoDataValue()
        invmatrix = np.array(ap.ReadAsArray()).astype(np.int64)
        bands = self.ds15.RasterCount
        if bands>1:#####################verify bands
            QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
            raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
        gtinv= self.ds15.GetGeoTransform()
        self.origineinv=[gtinv[0],gtinv[3]]
        self.winv=gtinv[1]
        self.hinv=gtinv[5]
        #################################dem
        # except:
        #     QgsMessageLog.logMessage("Failure to save sized inventory", tag="WoE")
        #     raise ValueError  # Failure to save sized inventory, see 'WoE' Log Messages Panel
        ###########################################load inventory
        self.catalog0=np.zeros(np.shape(invmatrix),dtype='int64')
        print(np.shape(invmatrix),'shape catalog')
        self.catalog0[:]=invmatrix[:]
        del invmatrix
        #######################################inventory from shp to tif
        fuori=self.vector2arrayinv(self.IN2a,self.inventory,self.catalog0)
        self.catalog=np.zeros(np.shape(fuori),dtype='int64')
        print(np.shape(fuori),'shape catalog')
        self.catalog[:]=fuori[:]
        del fuori




        #     dem_datas=self.vector2array(self.inventory,self.w,self.h,self.xmin,self.ymin,self.xmax,self.ymax,self.xsize,self.ysize)
        #     # write the data to output file
        #     rf1='/tmp/inv.tif'
        #     dem_datas1=np.zeros(np.shape(dem_datas),dtype='float32')
        #     dem_datas1[:]=dem_datas[:]#[::-1]
        #     w1=self.w
        #     h1=self.h*(-1)
        #     self.array2raster(rf1,w1,h1,dem_datas1,self.origine)##########rasterize inventory
        #     del dem_datas
        #     del dem_datas1
        #     ##################################
        #     IN1a=rf1
        #     IN2a='/tmp/invq.tif'
        #     IN3a=self.fold + '/inventorynxn.tif'
        #     self.cut(IN1a,IN2a,IN3a)########## inventory
        #     self.ds15=None
        #     self.ds15 = gdal.Open(IN3a)
        #     if self.ds15 is None:#####################verify empty row input
        #         QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
        #         raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
        #     ap=self.ds15.GetRasterBand(1)
        #     NoData=ap.GetNoDataValue()
        #     invmatrix = np.array(ap.ReadAsArray()).astype(np.int64)
        #     bands = self.ds15.RasterCount
        #     if bands>1:#####################verify bands
        #         QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
        #         raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
        #     #################################dem
        # # except:
        # #     QgsMessageLog.logMessage("Failure to save sized inventory", tag="WoE")
        # #     raise ValueError  # Failure to save sized inventory, see 'WoE' Log Messages Panel
        # ###########################################load inventory
        # self.catalog=np.zeros(np.shape(invmatrix),dtype='int64')
        # print(np.shape(invmatrix),'shape catalog')
        # self.catalog[:]=invmatrix[:]
        # del invmatrix
        ##del valuess
        ###########cause
        for v in range(countcause):
            ds8=gdal.Open(listcause[v],0)
            ds8x = ds8.RasterXSize
            ds8y = ds8.RasterYSize
            gt= ds8.GetGeoTransform()
            # causexl = round(gt[0],2)
            # causeyt = round(gt[3],2)
            # causexr = round(gt[0] + gt[1] * ds8x,2)
            # causeyb = round(gt[3] + gt[5] * ds8y,2)
            causexl = gt[0]
            causeyt = gt[3]
            causexr = gt[0] + gt[1] * ds8x
            causeyb = gt[3] + gt[5] * ds8y
            QgsMessageLog.logMessage(self.extent, tag="WoE")
            if (np.round(causexl,2))>(self.xmin) or (np.round(causexr,2))<(self.xmax) or (np.round(causeyb,2))>(self.ymin) or (np.round(causeyt,2))<(self.ymax):
                print(self.xmin,self.ymin,self.xmax,self.ymax,'selected extension')
                print(np.round(causexl,2),np.round(causeyb,2),np.round(causexr,2),np.round(causeyt,2),'cause extension')
                QgsMessageLog.logMessage('Cause %0.2f extension cannot satisfy selected extension' %v, tag="WoE")
                raise ValueError  # Cause extension cannot satisfy selected extension, see 'WoE' Log Messages Panel
            if self.w < abs(gt[1]) or self.h < abs(gt[5]):
                        QgsMessageLog.logMessage('Resolution requested is higher than Cause resolution', tag="WoE")
                        raise ValueError  # Resolution requested is higher than Cause resolution, see 'WoE' Log Messages Panel
            ds8=None
        ###################
        Causes={}
        id={}
        Mat={}
        dimensioni={}
        self.Wfs={}
        for i in range(countcause):
            #matrix=None
            self.Wcause=None
            self.classes=None
            self.Wcause=listcause[i]
            self.classes=listclasses[i]
            self.Wreclassed=None
            self.Wreclassed=self.fold+'/04reclassedcause'+str(i)+'.tif'
            pathszcause=None
            pathszcause=self.fold+'/01Wsizedcause'+str(i)+'.tif'
            # self.ds2=None
            # self.ds2 = gdal.Open(self.Wcause)
            # if self.ds2 is None:#####################verify empty row input
            #     QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
            #     raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            # gt=self.ds2.GetGeoTransform()
            # ww=gt[1]
            # hh=gt[5]
            # xyo=[gt[0],gt[3]]
            # a=self.ds2.GetRasterBand(1)
            # NoData=a.GetNoDataValue()
            # #self.RasterInt = np.array(a.ReadAsArray()).astype(int)
            # self.matrix = np.array(a.ReadAsArray()).astype(np.float32)
            # bands = self.ds2.RasterCount
            # if bands>1:#####################verify bands
            #     QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
            #     raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            # ################################################################
            # self.classification()#############
            # #del self.RasterInt
            # self.matrix1=np.zeros(np.shape(self.matrix2),dtype='float32')
            # self.matrix1[:]=self.matrix2[:]
            # #print(self.matrix[self.matrix==1])
            #
            # #print(max(self.matrix1,'max'))
            # #np.size(self.RasterInt1)
            # self.array2raster(pathszcause,ww,hh,self.matrix1,xyo)
            # del self.matrix2
            # del self.matrix1
            # #print(ciao)
            # ###################
            IN2='/tmp/02causeq'+str(i)+'.tif'
            IN1=self.Wcause
            IN3='/tmp/03causec'+str(i)+'.tif'
            IN4=pathszcause
            self.alignRaster(self.IN3a, IN1, IN2)
            self.cutextent(IN2,IN3,self.IN3a)
            self.cut(IN3,IN4)##############################
            if self.polynum==0:
                pathszcause=IN3
            #self.cutextent(IN2,IN3,self.IN3a)
            #self.cut(IN3,IN2,IN4)


            ################################################################
            self.ds2=None
            self.ds2 = gdal.Open(pathszcause)
            if self.ds2 is None:#####################verify empty row input
                QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
                raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            gt=self.ds2.GetGeoTransform()
            ww=gt[1]
            hh=gt[5]
            xyo=[gt[0],gt[3]]
            a=self.ds2.GetRasterBand(1)
            NoData=a.GetNoDataValue()
            #self.RasterInt = np.array(a.ReadAsArray()).astype(int)
            self.matrix = np.array(a.ReadAsArray()).astype(np.float32)
            idnul=np.where(self.matrix<=-9999)
            self.matrix[idnul]=-9999
            bands = self.ds2.RasterCount
            if bands>1:#####################verify bands
                QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
                raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            self.classification()#############
            #del self.RasterInt
            self.matrix1=np.zeros(np.shape(self.matrix2),dtype='float32')
            self.matrix1[:]=self.matrix2[:]
            #print(self.matrix[self.matrix==1])

            #print(max(self.matrix1,'max'))
            #np.size(self.RasterInt1)
            self.array2raster(self.Wreclassed,ww,hh,self.matrix1,xyo)
            del self.matrix2
            del self.matrix1
            #print(ciao)
            ###################



            #print(ciao)
            self.matrix=None
            self.RasterInt=None
            self.ds22=None
            self.ds22 = gdal.Open(self.Wreclassed)
            if self.ds22 is None:#####################verify empty row input
                QgsMessageLog.logMessage("ERROR: can't open raster input", tag="WoE")
                raise ValueError  # can't open raster input, see 'WoE' Log Messages Panel
            gt=self.ds22.GetGeoTransform()
            ww=gt[1]
            hh=gt[5]
            aa=self.ds22.GetRasterBand(1)
            NoData=aa.GetNoDataValue()
            self.RasterInt = np.array(aa.ReadAsArray()).astype(np.int64)
            print(np.max(self.RasterInt),'-1')
            self.matrix = np.array(aa.ReadAsArray()).astype(np.float32)
            bands = self.ds22.RasterCount
            if bands>1:#####################verify bands
                QgsMessageLog.logMessage("ERROR: input rasters shoud be 1-band raster", tag="WoE")
                raise ValueError  # input rasters shoud be 1-band raster, see 'WoE' Log Messages Panel
            ####################
            Causes[i]=self.RasterInt[:]
            print(np.max(self.RasterInt),'0')
            Mat[i]=self.matrix[:]
            id[i]=np.where(self.RasterInt<=-9999)
            idcat=np.where(self.catalog<=-9999)
            dimensioni[i]=np.shape(self.matrix)
            ##################################-9999
            del self.matrix
            del self.RasterInt
            #del out_bandC
            #del dataC

        for causa in range(countcause):
            self.Raster=np.array([])
            self.Matrix=np.array([])
            self.txtout=None
            self.Weightedcause=None
            self.txtout=self.fold+'/Wftxt'+str(causa)+'.txt'
            self.Weightedcause=self.fold+'/04weightedcause'+str(causa)+'.tif'
            self.ds10=None
            self.Raster=np.zeros(np.shape(Causes[causa]),dtype='int64')
            self.Raster[:]=Causes[causa]
            print(np.max(self.Raster),'1')
            self.Matrix=np.zeros(np.shape(Mat[causa]),dtype='float32')
            self.Matrix[:]=Mat[causa]
            self.Raster[idcat]=-9999
            self.Matrix[idcat]=-9999
            for cc in range(countcause):
                self.Raster[id[cc]]=-9999
                #print(np.max(self.Raster),'2')
                self.Matrix[id[cc]]=-9999
                self.catalog[id[cc]]=-9999
            if self.method==0:
                self.WoE()#################
            elif self.method==1:
                self.FR()##############
            self.Wfs[causa]=self.weighted[:]
            self.saveWf()##################
            self.weighted=np.array([])
        #del self.dem
        del self.catalog
        del Causes
        del Mat
        del id
        del self.Matrix
        del self.Raster

    def classification(self):###############classify causes according to txt classes
        Min={}
        Max={}
        clas={}
        with open(self.classes, 'r') as f:
            c = csv.reader(f,delimiter=' ')
            count=1
            for cond in c:
                b=np.array([])
                b=np.asarray(cond)
                Min[count]=b[0].astype(np.float32)
                Max[count]=b[1].astype(np.float32)
                clas[count]=b[2]#.astype(int)
                count+=1
        key_max=None
        key_min=None
        key_max = max(Max.keys(), key=(lambda k: Max[k]))
        key_min = min(Min.keys(), key=(lambda k: Min[k]))
        idx=np.where(np.isnan(self.matrix))
        self.matrix[idx]=-9999
        #self.RasterInt[idx]=-9999
        self.matrix[(self.matrix<Min[key_min])]=-9999
        #self.RasterInt[(self.RasterInt<Min[key_min])]=-9999
        self.matrix[(self.matrix>Max[key_max])]=-9999
        #self.RasterInt[(self.RasterInt>Max[key_max])]=-9999
        #del self.RasterInt

        self.matrix2=np.zeros(np.shape(self.matrix),dtype='float32')
        self.matrix2[:]=self.matrix[:]
        self.matrix2[self.matrix2==0]=-9999
        for i in range(1,count):
            self.matrix2[(self.matrix>=Min[i])&(self.matrix<Max[i])]=clas[i]
        del self.matrix


    def WoE(self):######################calculate W+,W-,Wf
        print('WoE')
        ################################################
        idx=[]
        idx1=[]
        idx2=[]
        idx3=[]
        idx=np.where(np.isnan(self.catalog))
        #print(len(self.catalog[self.catalog>-9999]),'catalog0')
        self.catalog[idx]=-9999
        ###############################################
        product=np.array([])
        diff=np.array([])
        #print(len(self.catalog[self.catalog>-9999]),'catalog')
        #print(len(self.Raster[self.Raster>-9999]),'raster')
        product=(self.catalog*self.Raster)
        #print(len(product),'lunghezza1')
        diff=(self.Raster-product)
        #print(len(diff),'lunghezza2')
        ######################################clean nan values
        idx2=np.where(self.catalog<=-9999)
        product[idx2]=-9999
        diff[idx2]=-9999
        diff[idx3]=-9999
        product[self.Raster<=-9999]=-9999
        #print(len(product[product>-9999]),'lunghezza1-1')
        diff[self.Raster<=-9999]=-9999
        #print(len(diff[self.Raster>-9999]),'lunghezza2-1')
        ############################################
        M=int(np.nanmax(self.Raster))
        print(M)
        #
        #
        countProduct = {}
        countDiff = {}
        #somma=0
        for n in range(0,M+1):
            P=np.array([])
            D=np.array([])
            PP=None
            DD=None
            #P=np.argwhere(product==float(n))
            P=np.where(product==float(n))
            PP=float(len(P[0]))
            #print(len(product[product>0]),'PP',n)
            #print(len(product[product==0]),'PP',n)
            #print(len(product[(product<1)&(product>-1)]),'PP',n)
            #print(len(product[product>-9999]),'PP',n)
            countProduct[n]=PP
            D=np.where(diff==float(n))
            DD=float(len(D[0]))
            #print(len(diff[diff>0]),'DD',n)
            #print(len(diff[diff==0]),'DD',n)
            countDiff[n]=DD
            #somma+= PP[n]
            print('product x class',n,countProduct[n])
            print('diff x class',n,countDiff[n])
            print('should be equal to:',len(product[product>-9999]))

        self.weighted=np.array([])
        self.weighted=np.zeros(np.shape(self.Matrix),dtype='float32')
        self.weighted[:]=self.Matrix[:]
        file = open(self.txtout,'w')#################save W+, W- and Wf
        file.write('class,Npx1,Npx2,Npx3,Npx4,W+,W-,Wf\n')
        print(M,'M')
        for i in range(1,M+1):

            Npx1=None
            Npx2=None
            Npx3=None
            Npx4=None
            Wplus=None
            Wminus=None
            Wf=None
            var=[]
            print('count', countProduct[i],countDiff[i])
            if countProduct[i]==0 or countDiff[i]==0:
                Wf=0.
                Wplus=0.
                Wminus=0.
                Npx1='none'
                Npx2='none'
                Npx3='none'
                Npx4='none'
                var=[i,Npx1,Npx2,Npx3,Npx4,Wplus,Wminus,Wf]
                file.write(','.join(str(e) for e in var)+'\n')
                self.weighted[self.Raster == i] = 0.
                print('class:',i)
                print(Npx1,':Npx1 ',Npx2,':Npx2 ',Npx3,':Npx3 ',Npx4,':Npx4 ')
                print(len(product[product>-9999]),'= Number of not null cells')

            else:
                Npx1=float(countProduct[i])
                for ii in range(1,M+1):
                    try:
                        Npx2 += float(countProduct[ii])
                        #Npx2 = Npx2+float(countProduct[ii])
                    except:
                        Npx2 = float(countProduct[ii])
                Npx2 -= float(countProduct[i])
                #Npx2 = Npx2-float(countProduct[i])
                Npx3=float(countDiff[i])
                for iii in range(1,M+1):
                    #
                    try:
                        Npx4 += float(countDiff[iii])
                        #Npx4 =  Npx4+float(countDiff[iii])
                    except:
                        Npx4 = float(countDiff[iii])
                Npx4 -= float(countDiff[i])
                #Npx4 = Npx4-float(countDiff[i])
                print('class:',i)
                print(Npx1,':Npx1 ',Npx2,':Npx2 ',Npx3,':Npx3 ',Npx4,':Npx4 ')
                print(len(product[product>-9999]),'= Number of not null cells')
                #
                if (Npx1+Npx2+Npx3+Npx4)==len(product[product>-9999]):
                    print(len(product[product>-9999]),'= Number of not null cells')
                else:
                    QgsMessageLog.logMessage("Failure to claculate Npx1,Npx2,Npx3,Npx4", tag="WoE")
                    raise ValueError  # Failure to claculate Npx1,Npx2,Npx3,Npx4, see 'WoE' Log Messages Panel
                #print(Npx1+Npx2+Npx3+Npx4,'sum')
                #W+ W-
                #Npx1,Npx2,Npx3,Npx4
                if Npx1==0 or Npx3==0:
                    Wplus=0.
                else:
                    Wplus=math.log((Npx1/(Npx1+Npx2))/(Npx3/(Npx3+Npx4)))
                if Npx2==0 or Npx4==0:
                    Wminus=0.
                else:
                    Wminus=math.log((Npx2/(Npx1+Npx2))/(Npx4/(Npx3+Npx4)))
                Wf=Wplus-Wminus
                var=[i,Npx1,Npx2,Npx3,Npx4,Wplus,Wminus,Wf]
                file.write(','.join(str(e) for e in var)+'\n')#################save W+, W- and Wf
                self.weighted[self.Raster == i] = Wf
                #
                #
        file.close()
        product=np.array([])
        diff=np.array([])

    def FR(self):######################calculate
        ################################################
        idx=[]
        idx1=[]
        idx2=[]
        idx3=[]
        idx=np.where(np.isnan(self.catalog))
        self.catalog[idx]=-9999
        ###############################################
        product=np.array([])
        clas=np.array([])
        product=(self.catalog*self.Raster)
        clas=self.Raster
        ######################################clean nan values
        idx2=np.where(self.catalog<=-9999)
        product[idx2]=-9999
        clas[idx2]=-9999
        clas[idx3]=-9999
        product[self.Raster<=-9999]=-9999
        clas[self.Raster<=-9999]=-9999
        ############################################
        M=int(np.nanmax(self.Raster))
        countProduct = {}
        countClass = {}
        for n in range(0,M+1):#verificare se n parte da 0 oppure da 1. e quindi stabilire il valore minimo delle classi ?????????????????????????
            P=np.array([])
            D=np.array([])
            P=np.argwhere(product==float(n))
            PP=float(len(P))
            #
            countProduct[n]=PP
            D=np.argwhere(clas==n)
            DD=float(len(D))
            countClass[n]=DD
        self.weighted=np.array([])
        self.weighted=self.Matrix
        file = open(self.txtout,'w')#################save W+, W- and Wf
        file.write('class,Npx1,Npx2,Npx3,Npx4,Wf\n')
        for i in range(1,M+1):
            Npx1=None
            Npx2=None
            Npx3=None
            Npx4=None
            Wplus=None
            Wminus=None
            Wf=None
            var=[]
            if countClass[i]==0:#if the class is not present or the landslides are not present then FR=0
                Wf=0.
                Npx1='none'
                Npx2='none'
                Npx3='none'
                Npx4='none'
                #Wplus=0.
                #Wminus=0.
                var=[i,Npx1,Npx2,Npx3,Npx4,Wf]
                file.write(','.join(str(e) for e in var)+'\n')
                self.weighted[self.Raster == i] = 0.
            else:
                Npx1=float(countProduct[i])
                Npx2=float(countClass[i])
                for ii in range(1,M+1):
                    try:
                        Npx3 += float(countProduct[ii])
                    except:
                        Npx3 = float(countProduct[ii])
                for iii in range(1,M+1):
                    try:
                        Npx4 += float(countClass[iii])
                    except:
                        Npx4 = float(countClass[iii])
                #W+ W-
                #Npx1,Npx2,Npx3,Npx4
                if Npx1==0:
                    Wf=0.
                else:
                    Wf=(np.divide((np.divide(Npx1,Npx2)),(np.divide(Npx3,Npx4))))
                var=[i,Npx1,Npx2,Npx3,Npx4,Wf]
                file.write(','.join(str(e) for e in var)+'\n') #################save W+, W- and Wf
                self.weighted[self.Raster == i] = float(Wf)
        file.close()
        product=np.array([])
        clas=np.array([])

    def saveWf(self):
        try:
            #out_data = None
            # read in data from first band of input raster
            cols = self.xsize
            rows = self.ysize
            self.weighted1=np.zeros(np.shape(self.weighted),dtype='float32')
            self.weighted1[:]=self.weighted[:]#[::-1]
            w2=self.winv
            h2=self.hinv
            self.array2raster(self.Weightedcause,w2,h2,self.weighted1,self.origineinv)
            del self.weighted
            del self.weighted1

        except:
            QgsMessageLog.logMessage("Failure to set nodata values on raster Wf", tag="WoE")
            raise ValueError  # Failure to set nodata values on raster Wf, see 'WoE' Log Messages Panel

    def sumWf(self):
        self.LSI=sum(self.Wfs.values())
        for iii in self.Wfs:
            idx=[]
            idx9=[]
            self.Wfs[iii]=self.Wfs[iii].astype(int)
            idx=np.where(np.isnan(self.Wfs[iii]))
            self.LSI[idx]=-9999
            self.LSI[self.LSI<=-9999]=-9999
            idx9=np.where(self.Wfs[iii]<=-9999)
            self.LSI[idx9]=-9999
        del self.Wfs

    def saveLSI(self):
        try:
            w3=self.winv
            h3=self.hinv
            self.array2raster(self.LSIout,w3,h3,self.LSI,self.origineinv)
            del self.LSI
        except:
            QgsMessageLog.logMessage("ERROR: Failure to set nodata values on raster LSI", tag="WoE")
            raise ValueError  # Failure to set nodata values on raster LSI, see 'WoE' Log Messages Panel

    def array2raster(self,newRasterfn,pixelWidth,pixelHeight,array,oo):
        cr=np.shape(array)
        cols=cr[1]
        rows=cr[0]
        originX = oo[0]
        originY = oo[1]
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(newRasterfn, int(cols), int(rows), 1, gdal.GDT_Float32)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(1)
        outband.SetNoDataValue(-9999)
        outband.WriteArray(array)
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(int(self.epsg[self.epsg.rfind(':')+1:]))
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
        print(cols,rows,originX, pixelWidth,originY, pixelHeight, 'array2raster')
        del array

    def alignRaster(self, raster, raster_to_align, output):
        #if os.path.isfile(output):
        #    os.remove(output)
        alignClass = QgsAlignRaster()
        item1 = QgsAlignRaster.Item(raster, "")
        item2 = QgsAlignRaster.Item(raster_to_align, output)
        alignClass.setRasters([item1, item2])
        alignClass.setParametersFromRaster(raster)
        rLyr = QgsRasterLayer(raster)
        clipExtent = rLyr.extent()
        alignClass.setClipExtent(clipExtent)
        alignClass.checkInputParameters()
        alignClass.createAndWarp(item2)

    def cutextent(self, in1, in2,raster):
        rlayer = QgsRasterLayer(raster, "layer")
        if not rlayer.isValid():
            print("Layer failed to load!")
        ext=rlayer.extent()#xmin
        xm = ext.xMinimum()
        xM = ext.xMaximum()
        ym = ext.yMinimum()
        yM = ext.yMaximum()
        pxlw=rlayer.rasterUnitsPerPixelX()
        pxlh=(rlayer.rasterUnitsPerPixelY())*(-1)
        newXNumPxl=(np.ceil(abs(xM-xm)/(rlayer.rasterUnitsPerPixelX()))-1).astype(int)
        newYNumPxl=(np.ceil(abs(yM-ym)/(rlayer.rasterUnitsPerPixelY()))-1).astype(int)
        sizex=newXNumPxl
        sizey=newYNumPxl
        origine=[xm,yM]
        if os.path.isfile(in2):
            os.remove(in2)
        os.system('gdal_translate -a_srs '+str(self.epsg)+' -a_nodata -9999 -of GTiff -ot Float32 -projwin ' +str(xm)+' '+str(yM)+' '+ str(xM) + ' ' + str(ym) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in1 +' '+in2)
        #processing.run('gdal:cliprasterbyextent', {'INPUT': in2,'PROJWIN': raster, 'NODATA': -9999, 'ALPHA_BAND': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3})

    def cut(self,in1,in3):
        print(self.newYNumPxl,self.newXNumPxl,'cause dimensions')
        if self.polynum==1:
            try:
                if os.path.isfile(in3):
                    os.remove(in3)

                #print(self.newYNumPxl,self.newXNumPxl,self.xmin,self.ymax,self.xmax,self.ymin)

                #os.system('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in1 +' '+in2)

                #processing.run('gdal:cliprasterbyextent', {'INPUT': in1,'PROJWIN': parameters['v'], 'NODATA': -9999, 'ALPHA_BAND': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3})

                        # alg_params = {
        #     'DATA_TYPE': 0,
        #     'EXTRA': '',
        #     'INPUT': parameters['r'],
        #     'NODATA': -9999,
        #     'OPTIONS': '',
        #     'PROJWIN': parameters['v'],
        #     'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        # }

                processing.run('gdal:cliprasterbymasklayer', {'INPUT': in1,'MASK': self.poly, 'NODATA': -9999, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3})

                #print('gdal:cliprasterbymasklayer', {'INPUT': in1,'MASK': self.poly, 'NODATA': -9999, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in2})

                #print('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in1 +' '+in2)
            except:
                QgsMessageLog.logMessage("Failure to save sized /tmp input", tag="WoE")
                raise ValueError  # Failure to save sized /tmp input Log Messages Panel
            # try:
            #     # if os.path.isfile(in3):
            #     #     os.remove(in3)
            #
            #     #os.system('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in2 +' '+in3)
            #
            #
            #     #print('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 '+ in2 +' '+in3)
            #
            #     #processing.run('gdal:cliprasterbymasklayer', {'INPUT': in2,'MASK': self.poly, 'NODATA': -9999, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3})
            #
            # except:
            #     QgsMessageLog.logMessage("Failure to save clipped input", tag="WoE")
            #     raise ValueError  # Failure to save sized /tmp input Log Messages Panel
        # else:
        #     try:
        #         if os.path.isfile(in3):
        #             os.remove(in3)
        #         if os.path.isfile(in2):
        #             os.remove(in2)
        #
        #         #os.system('gdalwarp -ot Float32 -q -of GTiff -t_srs '+str(self.epsg)+' -r bilinear '+ in1+' '+in2)
        #
        #         #print('gdalwarp -ot Float32 -q -of GTiff -t_srs '+str(self.epsg)+' -r bilinear '+ in1+' '+in2)
        #         #print(self.newYNumPxl,self.newXNumPxl,self.xmin,self.ymax,self.xmax,self.ymin)
        #
        #         #os.system('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + in1 +' '+in3)
        #
        #         #processing.run('gdal:cliprasterbymasklayer', {'INPUT': in1,'MASK': self.poly, 'NODATA': -9999, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': False, 'KEEP_RESOLUTION': True, 'MULTITHREADING': True, 'OPTIONS': '', 'DATA_TYPE': 6,'OUTPUT': in3}) modificare aggiungendo l'estenzione taglio
        #
        #
        #         print('gdal_translate -a_srs '+str(self.epsg)+' -of GTiff -ot Float32 -outsize ' + str(self.newXNumPxl) +' '+ str(self.newYNumPxl) +' -projwin ' +str(self.xmin)+' '+str(self.ymax)+' '+ str(self.xmax) + ' ' + str(self.ymin) + ' -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + in1 +' '+in3)
        #
        #     except:
        #         QgsMessageLog.logMessage("Failure to save sized input", tag="WoE")
        #         raise ValueError  # Failure to save sized /tmp input sized Log Messages Panel


    # def vector2array(self,inn,pxlw,pxlh,xm,ym,xM,yM,sizex,sizey):
    #     driverd = ogr.GetDriverByName('ESRI Shapefile')
    #     ds9 = driverd.Open(inn)
    #     layer = ds9.GetLayer()
    #     count=0
    #     for feature in layer:
    #         count+=1
    #         geom = feature.GetGeometryRef()
    #         xy=np.array([geom.GetX(),geom.GetY()])
    #         try:
    #             XY=np.vstack((XY,xy))
    #         except:
    #             XY=xy
    #     size=np.array([pxlw,pxlh])
    #     OS=np.array([xm,yM])
    #     NumPxl=(np.ceil(abs((XY-OS)/size)-1))#from 0 first cell
    #     #print(NumPxl)
    #     print(sizey,sizex,'dimensioni inventario')
    #     valuess=np.zeros((sizey,sizex),dtype='int64')
    #     #print(XY)
    #     #print(NumPxl)
    #     #print(len(NumPxl))
    #     #print(count)
    #     try:
    #         for i in range(count):
    #             #print(i,'i')
    #             if XY[i,1]<=yM and XY[i,1]>=ym and XY[i,0]<=xM and XY[i,0]>=xm:
    #                 valuess[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1
    #     except:#only 1 feature
    #         if XY[1]<=yM and XY[1]>=ym and XY[0]<=xM and XY[0]>=xm:
    #             valuess[NumPxl[1].astype(int),NumPxl[0].astype(int)]=1
    #     fuori = valuess.astype(np.float32)
    #     return fuori

    def vector2arrayinv(self,raster,lsd,invzero):
        rlayer = QgsRasterLayer(raster, "layer")
        if not rlayer.isValid():
            print("Layer failed to load!")
        ext=rlayer.extent()#xmin
        xm = ext.xMinimum()
        xM = ext.xMaximum()
        ym = ext.yMinimum()
        yM = ext.yMaximum()
        pxlw=rlayer.rasterUnitsPerPixelX()
        pxlh=(rlayer.rasterUnitsPerPixelY())*(-1)
        newXNumPxl=(np.ceil(abs(xM-xm)/(rlayer.rasterUnitsPerPixelX()))-1).astype(int)
        newYNumPxl=(np.ceil(abs(yM-ym)/(rlayer.rasterUnitsPerPixelY()))-1).astype(int)
        sizex=newXNumPxl
        sizey=newYNumPxl
        origine=[xm,yM]
        driverd = ogr.GetDriverByName('ESRI Shapefile')
        ds9 = driverd.Open(lsd)
        layer = ds9.GetLayer()
        self.ref = layer.GetSpatialRef()
        count=0
        for feature in layer:
            count+=1
            geom = feature.GetGeometryRef()
            xy=np.array([geom.GetX(),geom.GetY()])
            try:
                XY=np.vstack((XY,xy))
            except:
                XY=xy
        size=np.array([pxlw,pxlh])
        OS=np.array([xm,yM])
        NumPxl=(np.ceil(abs((XY-OS)/size)-1)).astype(int)#from 0 first cell
        print(NumPxl)
        print(sizey,sizex,'dimensioni inventario')
        valuess=np.zeros(np.shape(invzero),dtype='float32')
        try:
        #print(np.max(NumPxl[0,1]))
        #print(np.max(NumPxl[0,0]))
        #print(np.min(NumPxl[0,1]))
        #print(NumPxl[0,0])
        #print(count)
            for i in range(count):
                #print(i,'i')
                if XY[i,1]<=yM and XY[i,1]>=ym and XY[i,0]<=xM and XY[i,0]>=xm:
                    valuess[NumPxl[i,1].astype(int),NumPxl[i,0].astype(int)]=1
        except:#only 1 feature
            if XY[1]<=yM and XY[1]>=ym and XY[0]<=xM and XY[0]>=xm:
                valuess[NumPxl[1].astype(int),NumPxl[0].astype(int)]=1
        fuori = valuess.astype(np.float32)

        self.array2raster('/tmp/04inventory.tif',pxlw,pxlh,fuori,OS)
        return fuori
