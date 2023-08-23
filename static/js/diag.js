function mostrarDivSeleccionado() {
    let selectElement = document.getElementById("opciones");
    let selectedValue = selectElement.value;
    const vec = selectedValue.split("&=&");
    document.getElementById("tema").textContent = vec[0];
    document.getElementById("llave").textContent = vec[1];
    document.getElementById("unidad").textContent = vec[2];
    document.getElementById("tecnico").textContent = vec[3];
    document.getElementById("proyecto").textContent = vec[4];
    document.getElementById("fecha").textContent = vec[6];
    const coor = vec[5].split(",");
    showMap( coor[0],coor[1]);
    for (let i = 1; i <5;i++) {
        if (vec [i+6].length>6){
            document.getElementById("pi"+i).src = "https://drive.google.com/uc?id=" + vec[i+6].split("id=")[1];
            document.getElementById("pf"+i).src = "https://drive.google.com/uc?id=" + vec[i+10].split("id=")[1];
            console.log("https://drive.google.com/uc?id=" + vec[i+6].split("id=")[1]);
        }
    }
    document.getElementById("asistencia").src = "https://drive.google.com/uc?id=" + vec[15].split("id=")[1];
    document.getElementById("evento").src = "https://drive.google.com/uc?id=" + vec[16].split("id=")[1];
}
document.addEventListener('DOMContentLoaded', function () {
    const titulos = document.querySelectorAll('h1');
    const tablas = document.querySelectorAll('.comparable-table');
    titulos.forEach((titulo, index) => {
        titulo.addEventListener('click', function () {
            const tabla = tablas[index];
            const isTablaVisible = tabla.classList.contains('visible');
            tablas.forEach((tabla) => {
                if (tabla !== tablas[index]) {
                    tabla.classList.remove('visible');
                }
            });
            if (isTablaVisible) {
                tabla.classList.remove('visible');
            }
            else {
                tabla.classList.add('visible');
            }
        });
    });
});

function showMap(lat1, lon1) {
    let existingMap = document.getElementById("map");
    if (existingMap) {
        existingMap.remove();
    }
    let mapDiv = document.createElement("div");
    mapDiv.setAttribute("id", "map");
    mapDiv.setAttribute("style", "position:relative;width:100%;height:0;padding-bottom:60%;");
    document.querySelector("#k0").appendChild(mapDiv);
    let c = document.createElement("span");
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
    marker1.bindPopup("<div>Localización</div>");
    const markers = L.featureGroup([marker1]);
    map.fitBounds(markers.getBounds());
}

