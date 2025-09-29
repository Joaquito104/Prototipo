from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Venta
from .forms import ProductoForm


def _inventario_ctx():
    """
    Calcula filas de inventario (producto + ventas acumuladas) y totales globales
    en Python puro para evitar problemas de tipos en BD.
    """
    productos = list(Producto.objects.all().order_by("-id"))

    filas = []
    total_cantidad = 0
    total_monto = Decimal("0")

    for p in productos:
        ventas = list(p.ventas.all())
        ventas_cantidad = sum(v.cantidad for v in ventas)
        ventas_monto = sum(v.precio_total for v in ventas) if ventas else Decimal("0")

        filas.append({
            "obj": p,
            "ventas_cantidad": ventas_cantidad,
            "ventas_monto": ventas_monto,
        })

        total_cantidad += ventas_cantidad
        total_monto += ventas_monto

    return {
        "filas": filas,
        "total_cantidad": total_cantidad,
        "total_monto": total_monto,
    }


def menu_principal(request):
    """
    Menú con pestañas: ?tab=crear | lista | eliminar
    Mantiene la misma página y muestra el contenido debajo.
    """
    tab = request.GET.get("tab", "lista")  # por defecto 'lista'

    ctx = {"tab": tab}

    if tab in ("lista", "eliminar"):
        ctx.update(_inventario_ctx())
    if tab == "crear":
        ctx["form"] = ProductoForm()

    return render(request, "menu.html", ctx)


# --- Rutas “clásicas” opcionales (por compatibilidad) ---

def lista_productos(request):
    ctx = _inventario_ctx()
    return render(request, "productos/lista_productos.html", ctx)


def registrar_ventas(request):
    """
    Registra ventas en lote (una cantidad por producto) y descuenta stock.
    Redirige a 'next' si viene en POST/GET, o a la lista por defecto.
    """
    if request.method != "POST":
        return redirect("lista_productos")

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

        # Ajusta a stock disponible (o cambia por validación si prefieres)
        if cantidad > p.stock:
            cantidad = p.stock
        if cantidad <= 0:
            continue

        precio_unitario = Decimal(p.precio)
        precio_total = precio_unitario * cantidad

        Venta.objects.create(
            producto=p,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            precio_total=precio_total,
        )

        p.stock = p.stock - cantidad
        p.save(update_fields=["stock"])

    next_url = request.POST.get("next") or request.GET.get("next")
    return redirect(next_url or "lista_productos")


def crear_producto(request):
    """
    Crea producto y redirige a 'next' (si viene) o a la lista.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "lista_productos")
    else:
        form = ProductoForm()
    return render(request, "productos/crear_productos.html", {"form": form})


def eliminar_producto(request, pk):
    """
    Confirmación y eliminación de producto; vuelve a 'next' o a la lista.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        producto.delete()
        next_url = request.POST.get("next") or request.GET.get("next")
        return redirect(next_url or "lista_productos")

    return render(request, "productos/eliminar_productos.html", {"producto": producto})
