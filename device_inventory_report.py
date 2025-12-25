from extras.scripts import Script, ObjectVar, ChoiceVar
from dcim.models import Site, Rack, Device
from utilities.exceptions import AbortScript
import yaml
import os


# DEVICE INVENTORY REPORT SCRIPT
class DeviceInventoryReport(Script):

    # METADATA
    class Meta:
        name = "Device Inventory Report"
        description = "Filter devices and export result to YAML and PDF"

    # INPUT VARIABLES
    site = ObjectVar(model=Site, required=False)
    rack = ObjectVar(model=Rack, required=False)
    status = ChoiceVar(
        choices=[("active", "Active"), ("offline", "Offline")],
        required=True
    )
    
    # MAIN EXECUTION METHOD
    def run(self, data, commit=True):

        site = data.get("site")
        rack = data.get("rack")
        status = data["status"]

        # VALIDATION
        if not site and not rack:
            raise AbortScript("You must select at least Site or Rack.")

        # QUERYS
        queryset = Device.objects.filter(status=status)
        if site:
            queryset = queryset.filter(site=site)
        if rack:
            queryset = queryset.filter(rack=rack)
        queryset = queryset.order_by("id")

        results = []
        log_lines = []

        # LOGGING AND DATA COLLECTION
        for dev in queryset:
            rack_name = dev.rack.name if dev.rack else "No Rack"
            line = f"Site {dev.site.name} ({rack_name}): #{dev.id} - {dev.name}"
            self.log_info(line)
            log_lines.append(line)

            results.append({
                "id": dev.id,
                "name": dev.name,
                "site": dev.site.name,
                "rack": rack_name
            })

        # PDF GENERATION (SAFE)
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        human_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        pdf_path = f"/opt/netbox/netbox/reports_root/device_inventory_report_{timestamp}.pdf"

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # HEADER
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 40, "Device Inventory Report")

        c.setFont("Helvetica", 9)
        c.drawString(40, height - 60, f"Generated at: {human_date}")

        # Separator line
        c.line(40, height - 70, width - 40, height - 70)

        # BODY
        text = c.beginText(40, height - 100)
        c.setFont("Helvetica", 10)

        for line in log_lines:
            text.textLine(line)

        c.drawText(text)
        c.save()

        # SUCCESS MESSAGE
        self.log_success(f"PDF generated at {pdf_path}")
