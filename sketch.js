// http://www.geonames.org/export/
let distinctCities = []

let cityObjects = []


const mappa = new Mappa('Leaflet');
let trainMap;
let canvas;

let currentColor;

const options = {
  lat: 0,
  lng: 0,
  zoom: 1.5,
  style: "http://{s}.tile.osm.org/{z}/{x}/{y}.png"
}

function preload() {
  jobData = loadTable('dk-ch-se.csv', 'header');
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function setup() {
  canvas = createCanvas(windowWidth, windowHeight);
  trainMap = mappa.tileMap(options);
  trainMap.overlay(canvas);

  // gather all the distinct cities
  for (let row of jobData.rows) {
    if (!distinctCities.includes(row.get('City'))) {
      distinctCities.push(row.get('City'))
    }
  }

  for (let i = 0; i < distinctCities.length; i++) {
    if (distinctCities[i] == "Gothenburg") {
      console.log("fuck")
      distinctCities[i] = "Göteborg"
    }
  }

  // for each distinct city create an object
  distinctCities.forEach(element => {
    cityObjects.push({ city: element, num: 0, coordinates: getCoordinate(element) })
  });

  // increment number of jobs
  for (let row of jobData.rows) {
    cityObjects.forEach(element => {
      if (element.city == row.get('City')) {
        element.num += 1;
      }
    });
  }

  console.log(cityObjects)
  //getCoordinate('madrid').then((res) => console.log(res))
  currentColor = color(255, 0, 200, 100); // default color 
}

function getCoordinate(city) {
  let url = 'http://www.geonames.org/search.html?q=' + city + '&country='
  return fetch(url).then((res) => {
    return res.text();
  }).then((html) => {
    let el = document.createElement('html');
    el.innerHTML = html;
    //console.log(el.getElementsByClassName('restable')[0].children)
    lat = el.querySelector('#search > table > tbody > tr:nth-child(3) > td:nth-child(5)')
    lon = el.querySelector('#search > table > tbody > tr:nth-child(3) > td:nth-child(6)')
    let regex = /[0-9]+/g;
    let foundLat = lat.innerHTML.match(regex)
    let foundLon = lon.innerHTML.match(regex)
    finalLat = foundLat[0] + "." + foundLat[1] + foundLat[2]
    finalLon = foundLon[0] + "." + foundLon[1] + foundLon[2]
    return [finalLat, finalLon]
  })
}

function draw() {
    clear();
    for (let city of cityObjects) {
      city.coordinates.then((res) => {
        const pix = trainMap.latLngToPixel(res[0], res[1]);
        let jobCount = city.num
        let diameter = sqrt(jobCount)*4
        fill(255, 0, 200, 100);
        const zoom = trainMap.zoom();
        ellipse(pix.x, pix.y, diameter, diameter);
      })
    }
}
