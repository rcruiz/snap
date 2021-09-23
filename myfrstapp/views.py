from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
import xml.etree.ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from myfrstapp.models import proyectos,tipo
from statistics import mean
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import zipfile
import urllib
import csv

switch_datos={"forward": 1,
      "turn": 1,
      "turnLeft": 1,
      "setHeading": 1,
      " doFaceTowards": 1,
      "gotoXY": 1,
      "doGoToObject": 1,
      "doGlide": 1,
      "changeXPosition": 1,
      "setXPosition": 1,
      "changeYPosition": 1,
      "setYPosition": 1,
      "bounceOffEdge": 1,
      "doSwitchToCostume": 1,
      "doWearNextCostume": 1,
      "doSwitchToCostume": 1,
      "reportGetImageAttribute": 1,
      "reportNewCostumeStretched": 1,
      "reportNewCostume": 1,
      "changeEffect": 1,
      "changeScale": 1,
      "setScale": 1,
      "doSetVar": 2,
      "doChangeVar": 1,
      "doShowVar": 2,
      "doHideVar": 2,
      "doDeclareVariables": 2,
      "reportNewList": 3,
      "reportCONS": 3,
      "reportListItem": 3,
      "reportCDR": 3,
      "reportListLength": 3,
      "reportListIndex": 3,
      "reportListContainsItem": 3,
      "reportListIsEmpty": 3,
      "reportMap": 3,
      "reportKeep": 3,
      "reportFindFirst": 3,
      "reportCombine": 3,
      "reportConcatenatedLists": 3,
      "doAddToList": 3,
      "doDeleteFromList": 3,
      "doInsertInList": 3,
      "doReplaceInList": 3,
      "reportNumbers": 3}


switch_nivel= {
    0:'No level',
    1:'Basic',
    2:'Intermediate',
    3:'Advanced'
}

switch_interactividad= {
    'receiveGo':1,
    'receiveKey':1,
    'receiveInteraction':2,
    'reportTouchingObject':2,
    'reportKeyPressed':2,
    'doAsk':3,
    'reportTouchingObject':2,
    'reportTouchingColor':3,
    'reportColorIsTouchingColor':3,
    'reportMouseDown':3,
    'reportVideo':3,
    'reportGlobalFlag':3,
    'reportAudio':3,
}

switch_condicionales = {
    'doIf':1,
    'doIfElse':2,
    'reportIfElse':2,
    'reportAnd':3,
    'reportOr':3,
    'reportNot':3
}


#variables globales

user_tipo=''

# Create your views here.

def principal(request):
    return (render(request, 'home.html'))


def info(request):

    return (render(request, 'index.html'))
def show_project(request, name):
    if request.user.is_authenticated:
        data =  proyectos.objects.filter(usuario=request.user.username,name_proyecto=name)
        return(render(request, 'result.html',{'proyecto':list(data)[0], 'flag_url':True}))


@csrf_exempt
def dashboard(request):

    if request.user.is_authenticated:
        flag_estudiante=False
        if tipo.objects.get(usuario=request.user.username).tipo_usuario =='Estudiante':
            flag_estudiante=True
        if request.method=='GET':
            name_zip=None
            datos= calcular_datos(request,None)
        else:
            try:
                name_zip=request.POST['name_zip']
                datos=calcular_datos(request,name_zip)

            except:
                data1=calcular_datos(request,request.POST['name_zip1'])
                data2=calcular_datos(request,request.POST['name_zip2'])
                return (render(request, 'dashboard_comparing.html', {'data1':data1, 'data2':data2, 'zip1':request.POST['name_zip1'],'zip2':request.POST['name_zip2']}))

        return (render(request, 'dashboard.html', {'data':datos, 'flag_estudiante':flag_estudiante,'name_zip':name_zip}))


    else:

        return (render(request, 'please-login.html'))

@csrf_exempt
def dashboard_level(request, tag):
    level=tag.split('-')[0]
    print(level)
    zip=tag.split('-')[1]
    print(zip)
    print(request.user.username)
    if  zip=="None":
        print("hola")
        data =  proyectos.objects.filter(usuario=request.user.username,nivel=level, nombre_zip= None)
    else:
        data =  proyectos.objects.filter(usuario=request.user.username,nivel=level, nombre_zip= zip)

    print(data)
    return (render(request, 'dashboard_level.html',{'user_projects': data}))



@csrf_exempt
def analyze(request):
    flag_url=False

    if request.user.is_authenticated:
        estudiante=tipo.objects.get(usuario=request.user.username).tipo_usuario =='Estudiante'
        if request.method=='POST':
            if estudiante:
                flag_url=True
                try:
                    new_proyect=analyze_save_project(request)
                except:
                    return(render(request, 'error_analizar.html'))
                return(render(request, 'result.html',{'proyecto':new_proyect, 'flag_url':flag_url}))
            else:
                try:
                    new_proyect=analyze_save_project(request)
                    flag_url=True
                    return(render(request, 'result.html',{'proyecto':new_proyect,'flag_url':flag_url}))
                except:
                        flag_url=False
                        try:
                            user_projects,filename=analyze_save_zip(request)
                        except:
                            return(render(request, 'error_analizar_zip.html'))
                        return(render(request, 'result.html',{'filename':filename,'proyecto':user_projects,'flag_url':flag_url}))


        else:

            if estudiante:
                return (render(request, 'analyze-estudiantes.html'))
            else:
                return(render(request, 'simple_upload.html'))

    else:
        #no estas logeado
        if request.method=='POST':
            flag_url=True
            try:
                level,data,name_proyect = calcular_nivel(request.POST['url'])
            except:
                return(render(request, 'error_analizar.html'))
            print(urllib.parse.unquote(request.POST['url']))
            new_proyect={'url_proyecto':request.POST['url'], 'nivel': level,
            'condicionales':data[0], 'sincronizacion':data[1], 'control_flujo':data[2], 'abstraccion':data[3],'paralelismo':data[4],
            'categorias':data[5],'interactividad':data[6],'datos':data[7], 'name_proyecto':name_proyect}
            return(render(request, 'result.html',{'proyecto':new_proyect, 'flag_url':flag_url}))
        else:
            return (render(request, 'analyze-estudiantes.html'))

def contact(request):

    us=proyectos.objects.all()
    print(us)
    return (render(request, 'contact.html'))

def basic(request):
    return (render(request, 'basic.html'))

def intermediate(request):
    return (render(request, 'intermediate.html'))

def advanced(request):
    return (render(request, 'advanced.html'))

@csrf_exempt
def signup(request):
    global user_tipo
    mensaje=''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print('paso 3')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            #guardamos el tipo de usuario
            user_tipo=tipo(usuario=username, tipo_usuario=user_tipo)
            user_tipo.save()

            return HttpResponseRedirect('/login')
        else:
            return render(request, 'signup.html', {'form': form,'mensaje': mensaje})
    else:

        form = UserCreationForm()
        print('paso 2')
        return render(request, 'signup.html', {'form': form,'mensaje': mensaje})

@csrf_exempt
def choose(request):
    global user_tipo
    if request.POST:
        user_tipo= request.POST['tipo']
        print('paso 1')
        return HttpResponseRedirect('/signup')

    else:
        print('paso 0')
        return render(request, 'opcion_tipo_user.html')

@csrf_exempt
def login_user(request):
    if request.method=='POST':
        try:
            username=request.POST['username']
            password=request.POST['password']
            user=authenticate(username=username,password=password)
            if user !=None:
                login(request,user)
                return HttpResponseRedirect('/login')
            else:
                return HttpResponse('contraseña incorrecta')
        except:
            #poner AY ERROR 404
            return render(request,'login.html')

    else:
        return render(request,'login.html')

@csrf_exempt
def show_projects(request):
    flag_url=False
    flag_zip=False
    flag_estudiante=False
    msj=''
    user_projects= []
    if request.method=='GET':
        if request.user.is_authenticated:
                user_projects =  proyectos.objects.filter(usuario=request.user.username,nombre_zip=None)
                if tipo.objects.get(usuario=request.user.username).tipo_usuario=='Estudiante':
                    flag_estudiante=True
                if not user_projects:
                    flag_url= True
        else:
            return render(request,"please-login.html")
    else:
        if request.method=='POST':
            user_projects =  proyectos.objects.filter(usuario=request.user.username,nombre_zip=request.POST['name_zip'])
            if user_projects:
                flag_zip=True
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="file.csv"'
                writer = csv.writer(response)
                header = ['Name zip', 'Name project', 'Nivel', 'Abstraccion', 'Condicionales', 'Categorias', 'Control flujo',
                'Interactividad', 'Paralelismo', 'Sincronizacion', 'Datos']
                writer.writerow(header)
                for project in user_projects:
                    writer.writerow([project.nombre_zip, project.name_proyecto, project.nivel, project.abstraccion,
                    project.condicionales, project.categorias, project.control_flujo, project.interactividad,
                    project.paralelismo, project.sincronizacion,project.datos])
                return response
            else:
                msj='That file zip doesnt exit. Try again.'
    return render(request,'show_projects.html',{'user_projects':user_projects, 'flag_url': flag_url,
                    'flag_zip': flag_zip,'mensaje':msj, 'flag_estudiante': flag_estudiante})



@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

# /**************************************************************************************/
# funciones auxiliares

def calcular_datos(request,zip):
    basico=0
    intermedio=0
    avanzado=0
    nulo=0
    user_projects =  proyectos.objects.filter(usuario=request.user.username,nombre_zip=zip)
    for project in user_projects:
        if project.nivel=='Basic':
            basico=basico+1
        elif project.nivel=='Intermediate':
            intermedio=intermedio+1
        elif project.nivel=='Advanced':
            avanzado=avanzado+1
        else:
            nulo=nulo+1
    return [nulo, basico, intermedio,avanzado]

def analyze_save_project(request):

    level,data,name_proyect=calcular_nivel(request.POST['url'])
    name=urllib.parse.unquote(name_proyect)
    url_name="http://prodriguezmartin.pythonanywhere.com/project/"+name_proyect
    new_proyect=proyectos(usuario=request.user.username, url_proyecto=request.POST['url'], nivel= level,
    condicionales=data[0], sincronizacion=data[1], control_flujo=data[2], abstraccion=data[3],paralelismo=data[4],
    categorias=data[5],interactividad=data[6],datos=data[7],name_proyecto=name, url_name=url_name)
    new_proyect.save()
    return new_proyect

def analyze_save_zip(request):
    print('a')
    uploaded_file_url, archivos_xml, ruta, filename= save_extract_zip(request.FILES['myfile'],request)
    print('b')
    save_puntuacion_xml(archivos_xml, ruta, request,filename)
    print('c')
    user_projects =  proyectos.objects.filter(usuario=request.user.username,nombre_zip=filename)
    print('d')
    return user_projects, filename

def save_puntuacion_xml(archivos_xml, ruta, request, filename):
    for xml in archivos_xml:
        proyecto=xml.split('.')[0]
        if proyecto==xml:
            pass
        else:
            ruta_xml=ruta+'/'+xml
            puntuacion,data = calcular_puntuacion(ruta_xml)
            level=switch_nivel.get(puntuacion)
            name=urllib.parse.quote(proyecto)
            url_name="http://prodriguezmartin.pythonanywhere.com/project/"+name
            new_proyect=proyectos(usuario=request.user.username,name_proyecto=proyecto,url_proyecto=ruta_xml, nivel= level,
            condicionales=data[0], sincronizacion=data[1], control_flujo=data[2], abstraccion=data[3],paralelismo=data[4],
            categorias=data[5],interactividad=data[6],datos=data[7],nombre_zip=filename,url_name=url_name)
            new_proyect.save()
            print(level)


def save_extract_zip(myfile,request):

    fs = FileSystemStorage()
    filezip = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filezip)
    print(uploaded_file_url)
    filename=filezip.split('.')[0]
    print(filename)
    # open and extract all files in the zip OJOOOOOO PETARA EN pythonanywhere
    ruta_zip="/home/prodriguezmartin/snap" + uploaded_file_url
    ruta_extraccion = "/home/prodriguezmartin/snap/media/"+request.user.username + '&' + filename
    print(ruta_extraccion)
    password = None
    z = zipfile.ZipFile(ruta_zip, "r")
    try:
        archivos = z.namelist()
        print(archivos)
        z.extractall(pwd=password, path=ruta_extraccion)
    except:
        print('Error')
        pass
    z.close()
    return uploaded_file_url, archivos, ruta_extraccion, filename

def calcular_nivel(url):
    url1,name_proyect=parse_url(url)
    puntuacion, puntuaciones = calcular_puntuacion(url1)
    level=switch_nivel.get(puntuacion)
    print(level)
    return level, puntuaciones,name_proyect

def switch_puntuacion(media):
    if media <0.5:
        return 0
    elif media <1.5:
        return 1
    elif media <2.5:
        return 2
    else:
        return 3

def parse_url(url):
    s=url.split('=')
    #s1='https://snap.berkeley.edu/projects/'
    s1='https://cloud.snap.berkeley.edu/projects/'
    s2=s[1].split('&')[0]
    s3=s[2]
    url=s1+s2+'/'+s3
    print(url)
    print(s3)
    return url,s3

def calcular_puntuacion(url):
    parse_xml(url)
    condicionales =puntuacion_condicionales()
    sincronizacion=puntuacion_sincronizacion()
    flujo= control_flujo()
    abst=abstraccion()
    para=paralelismo()
    categ=categorias()
    interactividad=puntuacion_interactividad()
    datos=puntuacion_representacion_datos()
    data=(condicionales,sincronizacion,flujo,abst,para,categ,interactividad,datos)
    media=mean(data)
    print("La media es: " + str(media))
    print("El nivel es " + str(switch_puntuacion(media)))
    puntuacion = switch_puntuacion(media)
    return puntuacion, data

#mira si hay más de dos bloques en 1 script para control de flujo
def blocks_script(data):
    flag_anterior = 0
    flag_actual = 1
    resultado = False
    for element in data['sprites']:
        flag_actual = element['script']
        if flag_anterior == flag_actual:
            resultado = True
            break
        else:
            flag_anterior = element['script']

    return resultado
#numero de scripts
def number_script(data):

    try:
        n=data['sprites'][-1]['script']
        return n
    except:
        return 0

#numero de sprites
def number_sprite(data):
    try:
        n=data['sprites'][-1]['sprite']
        return n
    except:
        return 1


def paralelismo():

    #NO COMPRUEBO QUE RECIEVE ESTEN EN LOS DOS SPRITES... ????
    puntuacion_bajo = 0
    puntuacion_medio = 0
    puntuacion_avanzado = 0
    basic = False
    med = False
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)
    #calculamos los scripts y sprites
    n_script = number_script(data)
    n_sprite = number_sprite(data)
    #primera condicion tabla
    if  n_sprite == 1 and n_script >=2:
        basic =True
    elif n_sprite>=2 and n_script >=1:
        med = True
    #segunda condicion tabla
    for element in data['sprites']:
        if (element['block'] == 'receiveGo' or element['block'] == 'receiveKey')  and basic:
            puntuacion_bajo = 1
        elif (element['block'] == 'receiveGo' or element['block'] == 'receiveKey')  and med:
            puntuacion_medio= 2
        elif element['block'] =='receiveCondition' or element['block'] =='receiveMessage' or element['block'] =='receiveOnClone':
            puntuacion_avanzado = 3
            break
        else:
            pass
    return max(puntuacion_bajo, puntuacion_medio, puntuacion_avanzado)

def puntuacion_condicionales():
    mayor= 0
    actual = 0
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)
    #creamos un switch que nos de la  puntuación correspondiente
    for element in data['sprites']:
        actual = switch_condicionales.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor ==3:
                #mayor puntuacion no hace falta buscar mas
                break
    return mayor

def puntuacion_representacion_datos():
    mayor=0
    actual=0
    with open('/home/prodriguezmartin/snap/data.json') as file2:
        data = json.load(file2)
    for element in data['sprites']:
        actual = switch_datos.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor ==3:
                break

    return mayor

def puntuacion_interactividad():
    mayor= 0
    actual = 0
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)
    #creamos un switch que nos de la  puntuación correspondiente

    for element in data['sprites']:
        actual = switch_interactividad.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor ==3:
                break

    return mayor


def puntuacion_sincronizacion():
    mayor= 0
    actual = 0
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)
    #creamos un switch que nos de la  puntuación correspondiente
    switch_sincronizacion = {
        'doWait':1,
        'doBroadcast':2,
        'receiveMessage':2,
        'doStopThis':2,
        'doPauseAll':2,
        'doWaitUntil':3,
        'doBroadcastAndWait':3,
        'receiveCondition':3,
        'receiveOnClone':3
    }

    for element in data['sprites']:
        actual = switch_sincronizacion.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor ==3:
                break

    return mayor



def control_flujo():
    mayor= 0
    actual = 0
    puntuacion_bajo =0
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)

    if blocks_script(data):
        puntuacion_bajo = 1

    switch_flujo = {
        'doForever':2,
        'doRepeat':2,
        'doWaitUntil':3,
        'doUntil':3,
        'for':3
    }
    for element in data['sprites']:
        actual = switch_flujo.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor==3:
                break

    return max(puntuacion_bajo, mayor)


def abstraccion():
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)

    n_script = number_script(data)
    n_sprite = number_sprite(data)
    puntuacion_bajo = 0
    puntuacion_medio = 0
    puntuacion_avanzado = 0
    if  n_sprite == 1 and n_script >=2:
        puntuacion_bajo = 1
    elif n_sprite>=2 and n_script >=2:
        puntuacion_medio =2
    if  data['block-definition']:
        puntuacion_avanzado = 3


    #puntuacion ALTA BLOOCKS DEFINITION
    return max(puntuacion_bajo, puntuacion_medio, puntuacion_avanzado)

def categorias():
    dicc_categorias = {"motion": False, "looks": False, "sound": False, "pen": False, "control": False, "sensing": False, "operators": False, "variables": False}
    with open('/home/prodriguezmartin/snap/data.json') as file:
        data = json.load(file)
    with open('/home/prodriguezmartin/snap/all.json') as file2:
        diccionario_all= json.load(file2)

    for element in data['sprites']:
        categoria = diccionario_all.get(element['block'])
        dicc_categorias[categoria] = True
    puntuacion = 0
    categorias = dicc_categorias.values()
    for categoria in categorias:
        if categoria == True:
            puntuacion = puntuacion + 1
    if puntuacion <=2:
         return 1
    elif puntuacion>2 and puntuacion <=6:
        return 2
    else:
        return 3

def parse_xml(url):

    class myContentHandler(ContentHandler):
        def __init__ (self):
            self.inproject = False
            self.instage=False
            self.inSprites = False
            self.inScripts = False
            self.inBlock = False
            self.inScript = False
            self.inScript2 = False
            self.inSprite = False
            self.inVariables = False
            self.numberSprites = 0
            self.numberScripts = 0
            self.numberVariables = 0
            self.numberBlocks = 0
            self.inBlocks = False
            self.inContent = False
            self.theContent = ""
            self.inBlockDef=False
            self.numberBlockDef=0
            self.data = {}
            self.data['sprites'] = []
            self.data['variables'] = []
            self.data['block-definition']=[]
            self.inVariable = False
            self.inProject = False
            self.value=""

            self.inBlockCustom=False

        def startElement (self, name, attrs):

            global cont
            cont = 0
            if name == 'project':
                self.inProject= True
            elif self.inProject:
                if name == 'stage':
                    self.instage = True
                elif self.instage:
                    if name == 'sprites':
                        self.inSprites = True
                    elif self.inSprites:
                        if name == 'sprite':
                            self.inSprite =True
                            self.numberSprites = self.numberSprites + 1
                        elif self.inSprite:
                            if name == 'scripts':
                                self.inScripts=True
                            elif self.inScripts:
                                if name == 'script':
                                    try:
                                        value = attrs.getValue('x')
                                        self.inScript = True
                                        self.inScript2=False
                                        self.numberScripts = self.numberScripts + 1
                                    except:
                                        self.inScript = True
                                        self.inScript2=True
                                elif self.inScript or self.inScript2:
                                    if name == 'block':
                                        self.inBlock = True
                                        self.numberBlocks = self.numberBlocks + 1
                                        try:
                                            self.data['sprites'].append({
                                                'sprite': self.numberSprites,
                                                'script': self.numberScripts,
                                                'block': attrs.getValue('s'),
                                                'num_block':self.numberBlocks
                                                })

                                        except:
                                                self.inBlock = False
                                elif name=='block':
                                    self.inBlock = True
                                    self.numberBlocks = self.numberBlocks + 1
                                    try:
                                        self.data['sprites'].append({
                                            'sprite': self.numberSprites,
                                            'script': self.numberScripts,
                                            'block': attrs.getValue('s'),
                                            'num_block':self.numberBlocks
                                            })

                                    except:
                                            self.inBlock = False


                            elif name == 'blocks':
                                self.inBlocks = True
                            elif self.inBlocks:
                                #bloque definido
                                if name == 'block-definition':
                                    try:
                                        value = attrs.getValue('s')
                                        self.inBlockDef = True
                                        self.numberBlockDef= self.numberBlockDef + 1
                                        self.data['block-definition'].append({
                                            'name': value,
                                            'number': self.numberBlockDef,
                                            })
                                        self.data[value]=[]
                                        self.value = value
                                    except:
                                        self.inBlockDef = False
                                #guardamos los bloques usados en los bloques definidos
                                elif self.inBlockDef:

                                    self.inBlockCustom=True
                                    try:
                                        self.data[self.value].append({
                                            #'name': self.value,
                                            'block': attrs.getValue('s'),
                                            })
                                    except:
                                        self.inBlockCustom=False

                            elif name == 'variables':
                                self.inVariables = True
                            elif self.inVariables:
                                try:
                                    value = attrs.getValue('name')
                                    #print(value)
                                    self.numberVariables=self.numberVariables+1
                                    self.data['variables'].append({
                                        'variable': value,
                                        'number_var':self.numberVariables
                                        })
                                    self.inVariable = True
                                except:
                                    self.inVariable = False

                elif name == 'blocks':
                    self.inBlocks = True
                elif self.inBlocks:
                    if name == 'block-definition':
                        try:
                            self.value = attrs.getValue('s')
                            self.data[self.value]=[]
                            self.inBlockDef = True
                            self.numberBlockDef= self.numberBlockDef + 1
                            self.data['block-definition'].append({
                                'name': self.value,
                                'number': self.numberBlockDef
                                })

                        except:
                            self.inBlockDef = False

                    elif self.inBlockDef:
                        if name == 'block':
                            self.inBlockCustom=True
                            try:
                                self.data[self.value].append({
                                    #'name': self.value,
                                    'block': attrs.getValue('s'),
                                    })

                            except:
                                self.inBlockCustom=False

                elif name == 'variables':
                    self.inVariables = True

                elif self.inVariables:
                    try:
                        value = attrs.getValue('name')
                        print("variables" + value)
                        self.numberVariables=self.numberVariables+1
                        self.data['variables'].append({
                            'variable': value,
                            'number_var':self.numberVariables
                            })

                        self.inVariable = True

                    except:
                        self.inVariable = False

        #cerramos
        def endElement (self, name):

            #salimos del xml por lo que volcamos la información recogida en un JSON
            if name == 'project':
                self.inProject=False
                with open('/home/prodriguezmartin/snap/data.json', 'w') as file:
                    json.dump(self.data, file, indent=4)

            elif self.inProject:
                if name == 'stage':
                    self.instage=False

                elif  self.instage:
                    if name=='sprites':
                        self.inSprites=False

                    elif self.inSprites:

                        if name == 'blocks':
                            self.inBlocks = False

                        elif self.inBlocks:
                            if name== 'block-definition':
                                self.inBlockDef = False
                            elif self.inBlockDef:
                                self.inBlockCustom=False

                        elif name == 'variables':
                            self.inVariables=False

                        elif self.inVariable:
                            self.inVariables=False

                        elif name == 'sprite':
                            self.inSprite = False
                        elif self.inSprite:
                            if name == 'scripts':
                                self.inScripts=False
                            elif self.inScripts:
                                if name == 'script' and not self.inScript2:
                                    self.inScript = False
                                elif name == 'script' and self.inScript2:
                                    self.inScript2=False
                                elif self.inScript or self.inScript2:
                                    if name == 'block':
                                            self.inBlock = False
                                elif name=='block':

                                        self.inBlock = False
                elif name == 'blocks':
                    self.inBlocks = False
                elif self.inBlocks:
                    if name== 'block-definition':
                        self.inBlockDef = False
                    elif self.inBlockDef:
                        if name == 'block':
                            self.inBlockCustom = False

                elif name == 'variables':
                    self.inVariables=False
                elif self.inVariable:
                    self.inVariables=False





        def characters (self, chars):
            if self.inContent:
                self.theContent = self.theContent + chars


    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)

    theParser.parse(url)
