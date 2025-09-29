from decimal import Decimal
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
from .models import Producto, Venta
from .forms import ProductoForm

def menu_principal(request):
    return render(request, 'menu.html')

@require_http_methods(["GET"])
def lista_productos(request):
    productos = (
        Producto.objects
        .annotate(
            ventas_cantidad=Coalesce(Sum('ventas__cantidad'), 0),
            ventas_monto=Coalesce(Sum('ventas__precio_total'), 0),
        )
        .order_by('-id')
    )

    # suma de todas las ventas
    agregados = Venta.objects.aggregate(
        total_cantidad=Coalesce(Sum('cantidad'), 0),
        total_monto=Coalesce(Sum('precio_total'), 0),
    )

    ctx = {
        "productos": productos,
        "total_cantidad": agregados["total_cantidad"],
        "total_monto": agregados["total_monto"],
    }
    return render(request, "productos/lista.html", ctx)


@require_POST
def registrar_ventas(request):
    """
    Lee las cantidades a vender por producto desde el formulario,
    crea la Venta correspondiente, descuenta stock y redirige a la lista.
    """
    for p in Producto.objects.all():
        key = f"cantidad_{p.id}"
        raw = request.POST.get(key)
        if not raw:
            continue
        try:
            cantidad = int(raw)
        except ValueError:
            continue
        if cantidad <= 0:
            continue

        if p.stock < cantidad:
            cantidad = p.stock

        if cantidad <= 0:
            continue

        precio_unitario = Decimal(p.precio)
        precio_total = precio_unitario * cantidad

        # Crear la venta
        Venta.objects.create(
            producto=p,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            precio_total=precio_total,
        )

        p.stock = F('stock') - cantidad
        p.save(update_fields=["stock"])

    return redirect("lista_productos")

def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()  # crea y guarda en la base de datos
            return redirect('lista_productos')  # vuelve a la lista
    else:
        form = ProductoForm()
    return render(request, 'productos/crear_productos.html', {'form': form})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.delete()  # borra el producto de la base de datos
        return redirect('lista_productos')

    # Si el método es GET, solo muestra la página de confirmación
    return render(request, 'productos/eliminar_productos.html', {'producto': producto})