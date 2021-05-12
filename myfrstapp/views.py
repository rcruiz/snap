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



#variables globales
# Create your views here.

def principal(request):
    return (render(request, 'home.html'))


def info(request):

    return (render(request, 'info.html'))
@csrf_exempt
def analyze(request):
    #recibimos la url del proyecto
    if request.method=='POST':
        url1=request.POST['url']
        url=parse_url(url1)
        calcular_puntuacion(url)

    return (render(request, 'analyze.html'))

def contact(request):
    return (render(request, 'contact.html'))

def basic(request):
    return HttpResponse("Info de la pagina")

def intermediate(request):
    return HttpResponse("Info de la pagina")

def advanced(request):
    return HttpResponse("Info de la pagina")

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@csrf_exempt
def login_user(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user !=None:
            login(request,user)
        return HttpResponseRedirect('/')
    else:
        messages.add_message(request, messages.ERROR, "Incorrect user or password")
    return render(request,'login.html')
@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')



#funciones auxiliares
def parse_url(url):
    s=url.split('=')
    s1='https://snap.berkeley.edu/projects/'
    s2=s[1].split('&')[0]
    s3=s[2]
    url=s1+s2+'/'+s3
    print(url)
    return url

def calcular_puntuacion(url):
    #parse_xml('templates/intento1.xml')
    #parse_xml('https://snap.berkeley.edu/projects/msanch9474/AIR%20HOCKEY%20Final')
    parse_xml(url)
    print('condicionales ' + str(puntuacion_condicionales()))
    print('sincronizacion ' + str(puntuacion_sincronizacion()))
    print('control de flujo ' + str(control_flujo()))
    print('abstraccion ' + str(abstraccion()))
    print('paralelismo ' + str(paralelismo()))
    print('categorias ' + str(categorias()))
    print('interactividad ' + str(puntuacion_interactividad()))

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
    return data['sprites'][-1]['script']

#numero de sprites
def number_sprite(data):
    return data['sprites'][-1]['sprite']

def paralelismo():

    #NO COMPRUEBO QUE RECIEVE ESTEN EN LOS DOS SPRITES...
    puntuacion_bajo = 0
    puntuacion_medio = 0
    puntuacion_avanzado = 0
    basic = False
    med = False
    with open('data.json') as file:
        data = json.load(file)
    #calculamos los scripts y sprites
    n_script = number_script(data)
    n_sprite = number_sprite(data)

    if  n_sprite == 1 and n_script >=2:
        basic =True
    elif n_sprite>=2 and n_script >=1:
        med = True

    #falta hacer diccionario de esto
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
    with open('data.json') as file:
        data = json.load(file)
    #creamos un switch que nos de la  puntuación correspondiente
    switch_condicionales = {
        'doIf':1,
        'doIfElse':2,
        'reportIfElse':2,
        'reportAnd':3,
        'reportOr':3,
        'reportNot':3
    }

    for element in data['sprites']:
        actual = switch_condicionales.get(element['block'])
        if actual!= None and mayor < actual :
            mayor = actual
            if mayor ==3:
                break

    return mayor
def puntuacion_representacion_datos():

    with open('data1.json') as file:
        switch_datos = json.load(file)

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
    with open('data.json') as file:
        data = json.load(file)
    #creamos un switch que nos de la  puntuación correspondiente
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
    with open('data.json') as file:
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
    with open('data.json') as file:
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
    with open('data.json') as file:
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

    #puntuacion ALTA BLOOCKS DEFINITION
    return max(puntuacion_bajo, puntuacion_medio, puntuacion_avanzado)

def categorias():
    dicc_categorias = {"motion": False, "looks": False, "sound": False, "pen": False, "control": False, "sensing": False, "operators": False, "variables": False}
    with open('data.json') as file:
        data = json.load(file)
    with open('all.json') as file2:
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
                                            'name': self.value,
                                            'block': attrs.getValue('s'),
                                            })
                                    except:
                                        self.inBlockCustom=False

                            elif name == 'variables':
                                self.inVariables = True
                            elif self.inVariables:
                                try:
                                    value = attrs.getValue('name')
                                    print(value)
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
                            print("intentooo")
                            print(self.value)
                            try:
                                self.data[self.value].append({
                                    'name': self.value,
                                    'block': attrs.getValue('s'),
                                    })

                            except:
                                self.inBlockCustom=False

                elif name == 'variables':
                    self.inVariables = True

                elif self.inVariables:
                    try:
                        value = attrs.getValue('name')
                        print("hola" + value)
                        self.numberVariables=self.numberVariables+1
                        self.data['variables'].append({
                            'variable': value,
                            'number_var':self.numberVariables
                            })

                        print(self.data)
                        self.inVariable = True

                    except:
                        self.inVariable = False

        #cerramos
        def endElement (self, name):

            #salimos del xml por lo que volcamos la información recogida en un JSON
            if name == 'project':
                self.inProject=False
                with open('data.json', 'w') as file:
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
