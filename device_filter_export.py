from extras.scripts import Script, ObjectVar, ChoiceVar
from dcim.models import Site, Rack, Device
from django.core.exceptions import ValidationError
import yaml
from django.utils.text import slugify

class FilterDevicesScript(Script):
    pass

    site = ObjectVar(model=Site, required=False)
    rack = ObjectVar(model=Rack, required=False)
    status = ChoiceVar(
        choices=[("active", "Active"), ("offline", "Offline")],
        required=True
    )

    def run(self, data, commit=True):

        # Extraemos datos del formulario
        site = data.get("site")
        rack = data.get("rack")
        status = data["status"]

        # 1️⃣ Validación: al menos uno de los dos filtros
        if not site and not rack:
            raise ValidationError("Debe seleccionar al menos Site o Rack.")

        # 2️⃣ Construcción del queryset
        queryset = Device.objects.filter(status=status)

        if site:
            queryset = queryset.filter(site=site)

        if rack:
            queryset = queryset.filter(rack=rack)

        queryset = queryset.order_by("id")

        # 3️⃣ Generar log + preparar YAML
        results = []

        for dev in queryset:
            rack_name = dev.rack.name if dev.rack else "No Rack"
            line = f"Site {dev.site.name} ({rack_name}): #{dev.id} - {dev.name}"
            self.log_info(line)

            results.append({
                "id": dev.id,
                "name": dev.name,
                "site": dev.site.name,
                "rack": rack_name
            })

        # 4️⃣ Devolver YAML
        return yaml.dump(results, sort_keys=False)
