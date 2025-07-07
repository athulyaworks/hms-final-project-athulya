from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import PrescriptionItem, Medicine, Prescription

@receiver(pre_delete, sender=PrescriptionItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    medicine = instance.medicine
    new_stock = medicine.stock + instance.quantity
    if new_stock > medicine.max_stock:
        raise ValidationError(f"Cannot restore {medicine.name} beyond max stock ({medicine.max_stock}).")
    medicine.stock = new_stock
    medicine.save()

@receiver(pre_save, sender=PrescriptionItem)
def adjust_stock_on_update(sender, instance, **kwargs):
    if not instance.pk:
        # New item – stock will be reduced after creation in your view; skip signal
        return

    try:
        old_instance = PrescriptionItem.objects.get(pk=instance.pk)
    except PrescriptionItem.DoesNotExist:
        return

    quantity_diff = instance.quantity - old_instance.quantity
    medicine = instance.medicine

    if quantity_diff > 0:
        # More quantity needed, decrease stock
        if medicine.stock < quantity_diff:
            raise ValidationError(f"Insufficient stock for {medicine.name}.")
        medicine.stock -= quantity_diff
    elif quantity_diff < 0:
        # Reducing prescribed quantity → restore stock
        new_stock = medicine.stock + abs(quantity_diff)
        if new_stock > medicine.max_stock:
            raise ValidationError(f"Restoring stock exceeds max for {medicine.name}.")
        medicine.stock = new_stock

    medicine.save()

@receiver(pre_delete, sender=Prescription)
def restore_stock_on_prescription_delete(sender, instance, **kwargs):
    items = instance.prescriptionitem_set.all()
    for item in items:
        medicine = item.medicine
        new_stock = medicine.stock + item.quantity
        if new_stock > medicine.max_stock:
            raise ValidationError(f"Cannot restore {medicine.name} beyond max stock ({medicine.max_stock}).")
        medicine.stock = new_stock
        medicine.save()
