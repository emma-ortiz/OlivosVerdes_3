# app_fruteria/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from django.contrib.auth.forms import AuthenticationForm
import datetime 
import decimal
from decimal import Decimal
from .forms import RegistroClienteForm
from django.http import JsonResponse

# ====================================================================
# CORRECCIÓN: Importación de TODOS los Modelos de la App
# ====================================================================
from .models import (
    Producto, 
    Categoria, 
    Oferta, 
    PerfilCliente, 
    Sucursal,       # <-- Nuevo
    Compra,         # <-- Nuevo
    DetalleCompra ,  # <-- Nuevo
    Pedido,
    ItemPedido      # <-- Nuevo
)
from django.db.models import Q 

# --------------------------------------------------------------------------
# A. VISTAS DEL CATÁLOGO Y HOME
# --------------------------------------------------------------------------

def index(request):
    """
    Vista para la página principal (index.html).
    """
    productos_destacados = Producto.objects.all().order_by('-id')[:3] 
    
    contexto = {
        'productos_destacados': productos_destacados
    }
    return render(request, 'app_fruteria/index.html', contexto)

def menu_virtual(request):
    """
    Muestra el catálogo completo de productos (menu.html).
    """
    productos = Producto.objects.all().order_by('nombre')
    
    contexto = {
        'lista_productos': productos
    }
    return render(request, 'app_fruteria/menu.html', contexto)

def frutas_citricas(request):
    """
    Muestra solo las frutas de la categoría 'Cítricas' (citricas.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Cítricas').order_by('nombre')
    except:
        productos = Producto.objects.none()

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Cítricas'
    }
    return render(request, 'app_fruteria/citricas.html', contexto)

def frutas_dulces(request):
    """
    Muestra solo las frutas de la categoría 'Dulces' (dulces.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Dulces').order_by('nombre')
    except:
        productos = Producto.objects.none() 

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Dulces'
    }
    return render(request, 'app_fruteria/dulces.html', contexto)

def frutas_neutras(request):
    """
    Muestra solo las frutas de la categoría 'Neutras' (neutras.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Neutras').order_by('nombre')
    except:
        productos = Producto.objects.none() 

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Neutras'
    }
    return render(request, 'app_fruteria/neutras.html', contexto)

def ver_ofertas(request):
    """
    Muestra todos los productos que están asignados a ofertas activas y vigentes.
    """
    hoy = datetime.date.today()
    
    
    lista_productos_oferta = Producto.objects.filter(
        oferta__isnull=False,
        oferta__fecha_inicio__lte=hoy, 
        oferta__fecha_fin__gte=hoy
    ).order_by('nombre')

    # Solo enviamos la lista de productos
    contexto = {
        'lista_productos': lista_productos_oferta, # Cambiamos el nombre de la variable para que coincida con la plantilla
        'titulo_seccion': ' Ofertas y Promociones Vigentes'
    }

    
    return render(request, 'app_fruteria/ofertas.html', contexto)


# --------------------------------------------------------------------------
# B. VISTAS DE AUTENTICACIÓN
# --------------------------------------------------------------------------


def registro_usuario(request):
    """
    Maneja el registro de nuevos usuarios (inicios.html) usando un formulario seguro.
    """
    next_url = request.GET.get('next')  # Se define arriba para que esté disponible siempre

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, '¡Cuenta creada y sesión iniciada! Bienvenido a Olivos Verdes.')

            fallback_redirect = 'compra'  # Redirección por defecto
            return redirect(request.POST.get('next') or next_url or fallback_redirect)

        else:
            messages.error(request, 'Error en el registro. Por favor, verifica los datos.')
    else:
        form = RegistroClienteForm()

    contexto = {
        'form': form,
        'next': next_url
    }

    return render(request, 'app_fruteria/inicios.html', contexto)

def iniciar_sesion(request):
    """
    Maneja el inicio de sesión de usuarios existentes (login.html).
    """
    
    if request.method == 'POST':
        # 1. Crea el formulario CON los datos del POST
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # 2. Si es válido, obtén los datos limpios
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo! Sesión iniciada.')
                
                # 3. Redirige al 'next' o al menú
                return redirect(request.POST.get('next') or 'menu_virtual')
            else:
                # Esto es redundante (form.is_valid() ya lo checa) pero no hace daño
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            # 4. Si el formulario NO es válido, solo muestra el error
            messages.error(request, 'Usuario o contraseña incorrectos.')
            # El código continuará al render() de abajo,
            # pasando el 'form' que ya contiene los errores.

    else:
        # 5. Si es una petición GET, crea un formulario vacío
        form = AuthenticationForm()
        
    # 6. Renderiza la plantilla con el formulario
    # (ya sea el vacío del GET o el inválido del POST)
    form.fields['username'].label = 'Correo Electrónico'
    contexto = {'form': form}
    return render(request, 'app_fruteria/login.html', contexto)


@login_required 
def perfil_usuario(request):
    """ Muestra la información del usuario logueado (perfil.html). """
    # Esta parte es correcta y asume que el PerfilCliente existe (creado en registro_usuario)
    try:
        perfil = request.user.perfilcliente 
    except PerfilCliente.DoesNotExist:
        perfil = None 
        
    contexto = {
        'perfil': perfil,
        'usuario': request.user # También pasamos el objeto User
    }
    return render(request, 'app_fruteria/perfil.html', contexto)

def cerrar_sesion(request):
    """ Cierra la sesión del usuario. """
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio')


# --------------------------------------------------------------------------
# C. VISTAS DEL CARRITO Y COMPRA (Lógica con Sesiones de Django)
# --------------------------------------------------------------------------

def agregar_al_carrito(request, producto_id):
    """ 
    Añade un producto al carrito, aplicando el precio final (con descuento).
    """
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    
    # 🚨 CLAVE DE CORRECCIÓN: Usar la propiedad .precio_final para aplicar la oferta 🚨
    precio_a_guardar = str(producto.precio_final)
    
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
        cantidad_actual = carrito[producto_id_str]["cantidad"]
        # OPCIONAL: Actualizar el precio si la oferta cambió mientras estaba en el carrito
        carrito[producto_id_str]['precio'] = precio_a_guardar 
    else:
        carrito[producto_id_str] = {
            'cantidad': 1,
            'precio': precio_a_guardar # <-- Guarda el precio con descuento
        }
        cantidad_actual = 1
        
    request.session['carrito'] = carrito
    request.session.modified = True # Asegura que la sesión se guarde
    
    # --- LÓGICA DE RESPUESTA ---
    mensaje = f'✅ ¡{producto.nombre} añadido! Cantidad total: {cantidad_actual} kg.'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        return JsonResponse({ 
            'success': True,
            'message': mensaje,
            # No es necesario devolver totales aquí, pero sí en eliminar/ajustar
        })
    
    messages.success(request, mensaje)
    return redirect(request.META.get('HTTP_REFERER') or 'menu_virtual')

def ver_carrito(request):
    """
    Muestra los productos en el carrito (carrito.html) y calcula totales.
    """
    carrito = request.session.get('carrito', {})
    carrito_items = []
    total_general = 0
    costo_envio = 40.00 # Define el costo de envío
    
    for id_str, data in carrito.copy().items():
        try:
            producto = Producto.objects.get(pk=int(id_str))
            cantidad = data.get('cantidad', 0)
            precio = float(data.get('precio', 0))
            
            subtotal = cantidad * precio
            total_general += subtotal
            
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'precio_unitario': precio, 
            })
            
        except Producto.DoesNotExist:
            del carrito[id_str]
            request.session.modified = True 
        except ValueError:
            del carrito[id_str]
            request.session.modified = True
            messages.error(request, f"Error en el formato del precio del producto ID {id_str}. Eliminado del carrito.")

    request.session['carrito'] = carrito

    total_final = total_general + costo_envio

    contexto = {
        'carrito_items': carrito_items,
        'total_general': total_general,
        'costo_envio': costo_envio,
        'total_final': total_final, 
    }
    
    return render(request, 'app_fruteria/carrito.html', contexto)

def ajustar_cantidad(request, producto_id, accion):
    
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    
    if producto_id_str in carrito:
        cantidad_actual = carrito[producto_id_str]['cantidad']
        
        # OPCIONAL: Previene que el precio de oferta se pierda si la sesión es reescrita
        # Recuperamos el precio actual de la sesión (con descuento)
        precio_guardado = carrito[producto_id_str]['precio'] 
        
        if accion == 'aumentar':
            carrito[producto_id_str]['cantidad'] = cantidad_actual + 1
            messages.success(request, f"Cantidad de producto ID {producto_id} aumentada.")
            
        elif accion == 'disminuir':
            if cantidad_actual > 1:
                carrito[producto_id_str]['cantidad'] = cantidad_actual - 1
                messages.success(request, f"Cantidad de producto ID {producto_id} disminuida.")
            else:
                # Si la cantidad es 1 y se intenta disminuir, se elimina el ítem
                del carrito[producto_id_str]
                messages.info(request, f"Producto ID {producto_id} eliminado del carrito.")
                
        # Aseguramos que el precio de oferta original se mantenga en la sesión
        carrito[producto_id_str]['precio'] = precio_guardado

        # Guardar los cambios
        request.session['carrito'] = carrito
        request.session.modified = True 
        
    return redirect('ver_carrito')

# en app_fruteria/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, PerfilCliente, Pedido, ItemPedido # ¡Asegúrate de importar TODOS estos!

# en app_fruteria/views.py

@login_required 
def confirmar_compra(request):
    
    # --- Parte 1: Obtener carrito y perfil (para GET y POST) ---
    try:
        perfil_usuario = request.user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil_usuario = None 

    carrito_session = request.session.get('carrito', {})
    
    # --- Parte 2: Lógica de PROCESAR PAGO (cuando se presiona "PAGAR") ---
    if request.method == 'POST':
        
        # ... (Tu lógica de POST se queda igual) ...
        tarjeta_ingresada = request.POST.get('numero_tarjeta', '')
        
        if not tarjeta_ingresada:
            messages.error(request, 'Por favor, ingresa un número de tarjeta para continuar.')
            return redirect('confirmar_compra')

        if not carrito_session:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('menu_virtual')
        
        if not perfil_usuario or not perfil_usuario.direccion_entrega: 
            messages.error(request, 'Por favor, completa tu dirección de envío en tu perfil.')
            return redirect('perfil')

        try:
            nuevo_pedido = Pedido.objects.create(
                cliente=request.user,
                completado=True,
                pagado=True,
                id_transaccion_pago='sim_sandbox_' + request.user.username
            )
            
            for producto_id, item_data in carrito_session.items():
                try:
                    producto = Producto.objects.get(id=producto_id)
                    cantidad_real = int(item_data['cantidad'])
                    ItemPedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=producto,
                        cantidad=cantidad_real 
                    )
                except (Producto.DoesNotExist, TypeError, KeyError, ValueError):
                    continue
            
            del request.session['carrito']
            messages.success(request, '¡Tu pedido ha sido confirmado!')
            return redirect('orden_confirmada', pedido_id=nuevo_pedido.id)

        except Exception as e:
            messages.error(request, f'Error al guardar tu pedido: {e}')
            return redirect('confirmar_compra')

            
    # --- Parte 3: Lógica para MOSTRAR la página (petición GET) ---
    
    items_para_plantilla = []
    
    # ¡CORRECCIÓN IMPORTANTE! Inicia el subtotal como Decimal
    subtotal = Decimal('0.00')
    
    for producto_id, item_data in carrito_session.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            
            try:
                cantidad_real = int(item_data['cantidad'])
            except (TypeError, KeyError, ValueError):
                messages.error(request, f"Hubo un error al leer un producto de tu carrito.")
                continue

            # (Decimal * int) = Decimal
            total_item = producto.precio * cantidad_real
            # (Decimal + Decimal) = Decimal
            subtotal += total_item
            
            items_para_plantilla.append({
                'producto': producto,
                'cantidad': cantidad_real,
                'subtotal': total_item, 
            })
        except Producto.DoesNotExist:
            continue
    
    # --- ¡ESTA ES LA LÍNEA DEL ERROR! ---
    # ¡CORRECCIÓN! Convierte el costo de envío a Decimal
    costo_envio = Decimal('40.00') 
    
    # (Decimal + Decimal) = ¡FUNCIONA!
    total_con_envio = subtotal + costo_envio

    contexto = {
        'carrito_items': items_para_plantilla, 
        'total_general': subtotal,             
        'perfil': perfil_usuario,              
        'usuario': request.user,               
        'total_con_envio': total_con_envio,    
    }
    
    return render(request, 'app_fruteria/confirmar_compra.html', contexto)

@login_required
def orden_confirmada(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, cliente=request.user)
        contexto = { 'pedido': pedido }
        return render(request, 'app_fruteria/orden_confirmada.html', contexto)
    except Pedido.DoesNotExist:
        messages.error(request, 'No se encontró ese pedido.')
        return redirect('menu_virtual')
    

def eliminar_item_carrito(request, producto_id):
    """
    Elimina un producto del carrito, recalcula los totales y responde con JSON
    si es una solicitud AJAX para la actualización suave de la interfaz.
    """
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    producto_nombre = "Producto"
    costo_envio = 40.00 # Definimos el costo de envío aquí

    try:
        # Recuperamos el nombre del producto solo para el mensaje
        producto = Producto.objects.get(pk=producto_id)
        producto_nombre = producto.nombre
    except Producto.DoesNotExist:
        pass

    if producto_id_str in carrito:
        # 1. Eliminar el producto del diccionario
        del carrito[producto_id_str]
        request.session.modified = True
        
        mensaje = f'🗑️ {producto_nombre} ha sido eliminado de tu carrito.'
        
        # --- LÓGICA DE RESPUESTA AJAX ---
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            # 2. Recalcular el nuevo subtotal general
            nuevo_subtotal = 0
            for data in carrito.values():
                # Aseguramos que el precio se convierta a float y manejamos el caso por si falta la clave
                precio_item = float(data.get('precio', 0))
                cantidad_item = data.get('cantidad', 0)
                nuevo_subtotal += precio_item * cantidad_item
            
            # 3. Calcular el nuevo total final
            nuevo_total_final = nuevo_subtotal + costo_envio if nuevo_subtotal > 0 else 0.00
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'producto_id': producto_id,
                # 🚨 DEVOLVEMOS LOS NUEVOS TOTALES AL JAVASCRIPT 🚨
                'new_subtotal': nuevo_subtotal,
                'new_total_final': nuevo_total_final 
            })
        
        # --- FALLBACK DE REDIRECCIÓN DURA (Si no es AJAX) ---
        messages.success(request, mensaje)
        return redirect('ver_carrito')
    
    # Si el producto no estaba en el carrito
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'El producto ya no estaba en el carrito.'})
    
    messages.warning(request, 'El producto que intentas eliminar no se encontró en el carrito.')
    return redirect('ver_carrito')