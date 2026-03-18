const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const scriptPath = path.join(__dirname, 'json2ifc.py');
const outputDir = path.join(__dirname, 'output_IFC');

function runJson2Ifc(inputJson, outputIfc) {
  return spawnSync('python', [scriptPath, '--input_json', inputJson, '--output_ifc', outputIfc], {
    encoding: 'utf-8'
  });
}

describe('json2ifc pipeline integration tests', () => {
  test('Check for valid json file input', () => {
    // Functionality: check that input json is not empty
    const inputJson = 'C:/Users/iamsa/Downloads/scan2bim/output_instances/syn1/bim_reconstruction_data.json';
    expect(fs.existsSync(inputJson)).toBe(true);
    const jsonContent = fs.readFileSync(inputJson, 'utf-8');
    expect(jsonContent.trim().length).toBeGreaterThan(0);
    const jsonData = JSON.parse(jsonContent);
    expect(Array.isArray(jsonData)).toBe(true);
    expect(jsonData.length).toBeGreaterThan(0);
  });

  test('Check if valid IFC is generated', () => {
    // Functionality: check that IFC file is generated and not empty
    const inputJson = 'C:/Users/iamsa/Downloads/scan2bim/output_instances/syn1/bim_reconstruction_data.json';
    const outputIfc = path.join(outputDir, 'test_valid_wall.ifc');
    runJson2Ifc(inputJson, outputIfc);
    expect(fs.existsSync(outputIfc)).toBe(true);
    const ifcContent = fs.readFileSync(outputIfc, 'utf-8');
    expect(ifcContent.trim().length).toBeGreaterThan(0);
  });

  test('Check if all elements of json are converted to Ifc', () => {
    // Functionality: check that all elements from json are converted to IFC
    const inputJson = 'C:/Users/iamsa/Downloads/scan2bim/output_instances/syn1/bim_reconstruction_data.json';
    const outputIfc = path.join(outputDir, 'test_valid_wall.ifc');
    runJson2Ifc(inputJson, outputIfc);
    const jsonContent = fs.readFileSync(inputJson, 'utf-8');
    const jsonData = JSON.parse(jsonContent);
    const ifcContent = fs.readFileSync(outputIfc, 'utf-8');
    const wallCount = jsonData.filter(e => e.type === 'wall').length;
    const floorCount = jsonData.filter(e => e.type === 'floor').length;
    const ceilingCount = jsonData.filter(e => e.type === 'ceiling').length;
    const ifcWallCount = (ifcContent.match(/IFCWALL\(/gi) || []).length;
    const ifcSlabCount = (ifcContent.match(/IFCSLAB\(/gi) || []).length;
    const ifcCeilingCount = (ifcContent.match(/IFCCOVERING\(/gi) || []).length;
    expect(ifcWallCount).toBe(wallCount);
    expect(ifcSlabCount).toBe(floorCount);
    expect(ifcCeilingCount).toBe(ceilingCount);
  });

  test('Raise error if missing input JSON', () => {
    // Checks for missing input JSON file and raises error
    const inputJson = path.join(__dirname, 'input_json', 'missing_file.json');
    const outputIfc = path.join(outputDir, 'test_missing.ifc');
    const result = runJson2Ifc(inputJson, outputIfc);

    expect(result.status).not.toBe(0);
    expect(result.stderr).toMatch(/Input JSON not found/);
    expect(fs.existsSync(outputIfc)).toBe(false);
  });

  test('Raise error if missing geometric data', () => {
    // Checks for missing geometric data in wall and raises error
    const invalidJson = path.join(outputDir, 'invalid_wall.json');
    fs.writeFileSync(invalidJson, JSON.stringify({
      walls: [{ id: 'wall1', storey: 1, thickness: 0.2, height: 2.5 }]
    }));
    const outputIfc = path.join(outputDir, 'test_invalid_wall.ifc');
    const result = runJson2Ifc(invalidJson, outputIfc);

    expect(result.status).not.toBe(0);
    expect(result.stderr).toMatch(/KeyError|missing|geometry/);
    expect(fs.existsSync(outputIfc)).toBe(false);

    fs.unlinkSync(invalidJson);
  });
});
