const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const taxroll = require('./taxroll');

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

function cleanAddress(raw) {
  return raw
    .replace(/\([^)]*\)/g, '')
    .replace(/\b(lot|tract|parcel)\s*#?\s*\d+[a-z]?\b/gi, '')
    .replace(/#\s*\d+[a-z]?\b/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim()
    .replace(/^[,\s]+|[,\s]+$/g, '');
}

async function geocodeOnce(q) {
  const url = 'https://nominatim.openstreetmap.org/search?q=' + encodeURIComponent(q) + '&format=json&addressdetails=1&limit=1';
  const response = await fetch(url, { headers: { 'User-Agent': 'PropertyResearchTool/1.0' } });
  const data = await response.json();
  if (!data || data.length === 0) return null;
  return {
    lat: parseFloat(data[0].lat),
    lon: parseFloat(data[0].lon),
    displayName: data[0].display_name,
    details: data[0].address || {}
  };
}

async function getCoordinates(address) {
  try {
    const coordMatch = address.match(/^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$/);
    if (coordMatch) {
      const lat = parseFloat(coordMatch[1]);
      const lon = parseFloat(coordMatch[2]);
      const url = 'https://nominatim.openstreetmap.org/reverse?lat=' + lat + '&lon=' + lon + '&format=json&addressdetails=1';
      const response = await fetch(url, { headers: { 'User-Agent': 'PropertyResearchTool/1.0' } });
      const data = await response.json();
      return {
        lat: lat,
        lon: lon,
        displayName: (data && data.display_name) ? data.display_name : lat + ', ' + lon,
        details: (data && data.address) ? data.address : {},
        approximate: false
      };
    }

    const cleaned = cleanAddress(address);

    let hit = await geocodeOnce(cleaned);
    if (hit) { hit.approximate = false; return hit; }

    const noNumber = cleaned.replace(/^\s*\d+\s+/, '');
    if (noNumber !== cleaned) {
      hit = await geocodeOnce(noNumber);
      if (hit) { hit.approximate = true; return hit; }
    }

    const parts = cleaned.split(',').map(function(s){ return s.trim(); }).filter(Boolean);
    if (parts.length >= 2) {
      const cityState = parts.slice(-2).join(', ');
      hit = await geocodeOnce(cityState);
      if (hit) { hit.approximate = true; return hit; }
    }

    const zip = cleaned.match(/\b\d{5}\b/);
    if (zip) {
      hit = await geocodeOnce(zip[0] + ', TX');
      if (hit) { hit.approximate = true; return hit; }
    }

    return null;
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
}

async function checkFloodZone(lat, lon) {
  try {
    const base = 'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query';
    const url = base
      + '?geometry=' + lon + ',' + lat
      + '&geometryType=esriGeometryPoint&inSR=4326'
      + '&spatialRel=esriSpatialRelIntersects'
      + '&outFields=FLD_ZONE,ZONE_SUBTY,STATIC_BFE,DEPTH,SFHA_TF'
      + '&returnGeometry=false&f=json';

    const response = await fetch(url);
    const data = await response.json();

    if (!data.features || data.features.length === 0) {
      return {
        floodZone: 'No FEMA zone mapped at this point',
        floodSubtype: null,
        bfe: null,
        inSFHA: null,
        floodRisk: 'unknown'
      };
    }

    const a = data.features[0].attributes;
    const zone = a.FLD_ZONE || 'Unknown';
    const subtype = a.ZONE_SUBTY || null;
    const sfha = a.SFHA_TF === 'T';

    let bfe = null;
    if (a.STATIC_BFE && a.STATIC_BFE > -9999) {
      bfe = Math.round(a.STATIC_BFE) + ' ft';
    } else if (a.DEPTH && a.DEPTH > -9999) {
      bfe = a.DEPTH + ' ft depth';
    }

    let risk = 'low';
    if (/^(A|V)/.test(zone)) {
      risk = 'high';
    } else if (subtype && /floodway/i.test(subtype)) {
      risk = 'high';
    } else if (zone === 'X' && subtype && /0\.2|shaded/i.test(subtype)) {
      risk = 'moderate';
    }

    return {
      floodZone: zone,
      floodSubtype: subtype,
      bfe: bfe,
      inSFHA: sfha,
      floodRisk: risk
    };
  } catch (error) {
    console.error('Flood zone error:', error);
    return {
      floodZone: 'Unable to verify',
      floodSubtype: null,
      bfe: null,
      inSFHA: null,
      floodRisk: 'unknown'
    };
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

function generateLeveragePoints(floodRisk, taxStatus) {
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
  if (taxStatus && taxStatus.delinquent) {
    const r = taxStatus.record;
    points.push('TAX DELINQUENT - $' + r.totalOwed.toLocaleString('en-US') + ' owed across ' + r.yearsOwed + ' year' + (r.yearsOwed === 1 ? '' : 's'));
    if (r.outOfStateOwner) points.push('Out-of-state owner (mails to ' + r.mailState + ') - likely absentee');
  } else if (taxStatus && taxStatus.matchAttempted) {
    points.push('Not on county delinquent tax list');
  } else {
    points.push('Pull tax record for delinquencies');
  }
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
    // An approximate geocode is a street or town, not the parcel, so don't claim a tax match.
    const taxStatus = countyKey && taxroll.isSupported(countyKey) && !coords.approximate
      ? taxroll.lookup(countyKey, coords.details.house_number, coords.details.road)
      : null;

    res.json({
      success: true,
      data: {
        address: coords.displayName,
        coordinates: coords.lat.toFixed(5) + ', ' + coords.lon.toFixed(5),
        approximate: coords.approximate,
        mapsLink: 'https://maps.google.com/?q=' + coords.lat + ',' + coords.lon,
        county: countyConfig ? countyConfig.name : 'County not detected',
        countyDetected: Boolean(countyConfig),
        taxUrl: countyConfig ? countyConfig.taxUrl : null,
        cadUrl: countyConfig ? countyConfig.cadUrl : null,
        floodZone: floodData.floodZone,
        floodSubtype: floodData.floodSubtype,
        bfe: floodData.bfe,
        inSFHA: floodData.inSFHA,
        floodRisk: floodData.floodRisk,
        taxStatus: taxStatus,
        leveragePoints: generateLeveragePoints(floodData.floodRisk, taxStatus)
      }
    });
  } catch (error) {
    console.error('Research error:', error);
    res.status(500).json({ error: 'Error researching property. Try again.' });
  }
});

function csvCell(v) {
  const s = v === null || v === undefined ? '' : String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

app.get('/api/delinquent.csv', (req, res) => {
  const county = String(req.query.county || '').toLowerCase();
  if (!taxroll.isSupported(county)) {
    return res.status(400).json({ error: 'Bulk tax data is only available for dallas and tarrant' });
  }
  const leads = taxroll.filterLeads(county, {
    minOwed: parseFloat(req.query.minOwed) || 0,
    minYears: parseInt(req.query.minYears, 10) || 0,
    zip: (req.query.zip || '').trim()
  });
  const header = ['Account', 'Owner', 'Property Address', 'Property Zip', 'Mailing Address', 'Mailing City', 'Mailing State', 'Mailing Zip', 'Total Owed', 'Years Owed', 'Tax Years', 'Out of State Owner', 'County'];
  const countyName = taxroll.COUNTIES[county].name;
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="delinquent-' + county + '.csv"');
  res.write(header.join(',') + '\n');
  for (const r of leads) {
    res.write([r.account, r.owner, r.propertyAddress, r.propertyZip, r.mailingAddress, r.mailCity, r.mailState, r.mailZip,
      r.totalOwed.toFixed(2), r.yearsOwed, r.years.join(' '), r.outOfStateOwner ? 'Yes' : 'No', countyName].map(csvCell).join(',') + '\n');
  }
  res.end();
});

app.get('/api/taxroll/status', (req, res) => {
  res.json(taxroll.status());
});

taxroll.start();

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('Property Research Tool running on port ' + PORT);
});
