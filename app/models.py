from django.db import models
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.SmallIntegerField()   # Precio en CLP (entero pequeño)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre
class Venta(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='ventas'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.producto.nombre}"
