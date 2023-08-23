  // Función para mostrar el pop-up
  function showPopup(event, elementId) {
    const popup = document.getElementById("popup");
    popup.style.display = "block";
    popup.style.left = event.pageX + "px";
    popup.style.top = event.pageY + "px";
    document.getElementById("image").src = "https://drive.google.com/uc?id=" + elementId;
  }
  function clearMap(mapId) {
    var mapContainer = document.getElementById(mapId);
    while (mapContainer.firstChild) {
        mapContainer.removeChild(mapContainer.firstChild);
    }
}
  function showPopup1(event, element, s) {
    const popup = document.getElementById('k0');
    popup.style.display = "block";
    popup.style.left = event.pageX + "px";
    popup.style.top = event.pageY + "px";
    const coor =  s.split(",");
    if (coor.length>3){
      showMap(coor[0], coor[1], coor[2], coor[3]);
    }else{
      showMap(coor[0], coor[1], coor[0], coor[1]);
    }

    }

  // Función para filtrar la tabla
  function filterTable() {
    const filterValues = [];
    const filterInputs = document.getElementsByClassName("filter-input");

    for (let i = 0; i < filterInputs.length; i++) {
      filterValues[i] = filterInputs[i].value.toUpperCase();
    }

    const table = document.getElementById("myTable");
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].getElementsByTagName("td");
      let visible = true;

      for (let j = 0; j < filterValues.length; j++) {
        const cell = cells[j];
        if (cell) {
          const cellValue = cell.textContent || cell.innerText;
          if (cellValue.toUpperCase().indexOf(filterValues[j]) === -1) {
            visible = false;
            break;
          }
        }
      }

      rows[i].style.display = visible ? "" : "none";
    }
  }

  // Función para ocultar los pop-ups cuando se hace clic fuera de ellos
  document.addEventListener("click", function (event) {
    const popups = document.getElementsByClassName("popup");
    const target = event.target;

    // Comprobar si el clic ocurrió fuera de cualquier elemento con la clase "popup"
    if (!target.closest(".popup") && !target.closest("span")) {
      for (let i = 0; i < popups.length; i++) {
        popups[i].style.display = "none";
      }
    }
  });

  // Asignar eventos a los campos de filtro
  const titles = ["Llave de gira", "Unidad", "Técnico", "Objetivo", "Vehículo", "Placa", "Recorrido", "Km inicial", "Km final", "Observaciones"];
  const filterInputs = document.getElementsByClassName("filter-input");

  for (let i = 0; i < titles.length; i++) {
    filterInputs[i].addEventListener('input', filterTable);
    filterInputs[i].placeholder = titles[i];
  }

  function showMap(lat1, lon1, lat2, lon2) {
     var existingMap = document.getElementById("map");
    if (existingMap) {
        existingMap.remove();
    }

    var mapDiv = document.createElement("div");
    mapDiv.setAttribute("id", "map");
    mapDiv.setAttribute("style", "position:relative;width:100%;height:0;padding-bottom:60%;");
    document.querySelector("#k0").appendChild(mapDiv);
    var c = document.createElement("span");
    c.setAttribute("style","color:#565656");
    c.textContent="Make this Notebook Trusted to load map: File -> Trust Notebook"
    document.querySelector("#map").appendChild(c);
    const map = L.map("map", {
        center: [lat1, lon1],
        crs: L.CRS.EPSG3857,
        zoom: 8,
        zoomControl: true,
        preferCanvas: false,
    });

    L.control.scale().addTo(map);

    const tile_layer = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: "Data by &copy; <a target=\"_blank\" href=\"http://openstreetmap.org\">OpenStreetMap</a>, under <a target=\"_blank\" href=\"http://www.openstreetmap.org/copyright\">ODbL</a>.",
            detectRetina: false,
            maxNativeZoom: 18,
            maxZoom: 18,
            minZoom: 0,
            noWrap: false,
            opacity: 1,
            subdomains: "abc",
            tms: false,
        }
    ).addTo(map);

    const marker1 = L.marker([lat1, lon1]).addTo(map);
    marker1.bindPopup("<div>Inicio</div>");

    const marker2 = L.marker([lat2, lon2]).addTo(map);
    marker2.bindPopup("<div>Fin</div>");

    // Fit the map to the bounds of the markers
    const markers = L.featureGroup([marker1, marker2]);
    map.fitBounds(markers.getBounds());

}
