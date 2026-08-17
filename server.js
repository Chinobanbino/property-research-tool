const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const COUNTY_CONFIG = {
  'kaufman': {
    name: 'Kaufman County',
    taxUrl: 'https://www.kaufmancad.org/',
    cadUrl: 'https://www.kaufmancad.org/property-search/'
  },
  'dallas': {
    name: 'Dallas County',
    taxUrl: 'https://www.dallascad.org/',
    cadUrl: 'https://www.dallascad.org/SearchAddr.aspx'
  },
  'tarrant': {
    name: 'Tarrant County',
    taxUrl: 'https://www.tarrantcad.org/',
    cadUrl: 'https://www.tarrantcad.org/property-search/'
  },
  'henderson': {
    name: 'Henderson County',
    taxUrl: 'https://www.henderson-cad.org/',
    cadUrl: 'https://www.henderson-cad.org/property-search/'
  },
  'grayson': {
    name: 'Grayson County',
    taxUrl: 'https://www.graysonappraisal.org/',
    cadUrl: 'https://www.graysonappraisal.org/property-search/'
  },
  'howard': {
    name: 'Howard County',
    taxUrl: 'https://www.howardcad.org/',
    cadUrl: 'https://www.howardcad.org/property-search/'
  },
  'montague': {
    name: 'Montague County',
    taxUrl: 'https://www.montaguecad.org/',
    cadUrl: 'https://www.montaguecad.org/property-search/'
  }
};

async function getCoordinates(address) {
  try {
    const url = 'https://nominatim.openstreetmap.org/search?q=' + encodeURIComponent(address) + '&format=json&addressdetails=1&limit=1';
    const response = await fetch(url, { headers: { 'User-Agent': 'PropertyResearchTool/1.0' } });
    const data = await response.json();
    if (!data || data.length === 0) return null;
    return {
      lat: parseFloat(data[0].lat),
      lon: parseFloat(data[0].lon),
      displayName: data[0].display_name,
      details: data[0].address || {}
    };
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
}

async function checkFloodZone(lat, lon) {
  try {
    const url = 'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query?geometry=' + lon + ',' + lat + '&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=FLD_ZONE,ZONE_SUBTY&returnGeometry=false&f=json';
    const response = await fetch(url);
    const data = await response.json();

    if (data.features && data.features.length > 0) {
      const zone = data.features[0].attributes.FLD_ZONE || 'Unknown';
      const highRisk = /^(A|V)/.test(zone);
      return {
        floodZone: zone,
        floodRisk: highRisk ? 'high' : 'low'
      };
    }
    return { floodZone: 'No FEMA zone mapped', floodRisk: 'unknown' };
  } catch (error) {
    console.error('Flood zone error:', error);
    return { floodZone: 'Unable to verify', floodRisk: 'unknown' };
  }
}

function detectCounty(coords) {
  const county = (coords.details.county || '').toLowerCase();
  for (const key of Object.keys(COUNTY_CONFIG)) {
    if (county.includes(key)) return key;
  }
  const nameLower = coords.displayName.toLowerCase();
  for (const key of Object.keys(COUNTY_CONFIG)) {
    if (nameLower.includes(key)) return key;
  }
  return null;
}

function generateLeveragePoints(floodRisk) {
  const points = [];
  if (floodRisk === 'high') {
    points.push('HIGH FLOOD RISK - major negotiation leverage');
  } else if (floodRisk === 'low') {
    points.push('Flood zone clear');
  } else {
    points.push('Flood zone unverified - check FEMA manually');
  }
  points.push('Verify lot shape and topography in GIS');
  points.push('Confirm road access - check for landlocked');
  points.push('Pull tax record for delinquencies');
  return points;
}

app.post('/api/research', async (req, res) => {
  const { address } = req.body;

  if (!address || address.trim() === '') {
    return res.status(400).json({ error: 'Enter a property address' });
  }

  try {
    const coords = await getCoordinates(address);
    if (!coords) {
      return res.status(404).json({ error: 'Property not found. Include city and state.' });
    }

    const countyKey = detectCounty(coords);
    const countyConfig = countyKey ? COUNTY_CONFIG[countyKey] : null;
    const floodData = await checkFloodZone(coords.lat, coords.lon);

    res.json({
      success: true,
      data: {
        address: coords.displayName,
        coordinates: coords.lat.toFixed(5) + ', ' + coords.lon.toFixed(5),
        mapsLink: 'https://maps.google.com/?q=' + coords.lat + ',' + coords.lon,
        county: countyConfig ? countyConfig.name : 'County not detected',
        countyDetected: Boolean(countyConfig),
        taxUrl: countyConfig ? countyConfig.taxUrl : null,
        cadUrl: countyConfig ? countyConfig.cadUrl : null,
        floodZone: floodData.floodZone,
        floodRisk: floodData.floodRisk,
        leveragePoints: generateLeveragePoints(floodData.floodRisk)
      }
    });
  } catch (error) {
    console.error('Research error:', error);
    res.status(500).json({ error: 'Error researching property. Try again.' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('Property Research Tool running on port ' + PORT);
});
