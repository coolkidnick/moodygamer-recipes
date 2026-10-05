#!/usr/bin/env node
/**
 * Validate MoodyGamer recipes against schema/recipe.schema.json
 * Node only — no npm dependencies. Minimal Draft-2020-12 subset.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SCHEMA_PATH = path.join(ROOT, 'schema', 'recipe.schema.json');
const RECIPES_DIR = path.join(ROOT, 'recipes');

function fail(msg) {
  console.error('FAIL:', msg);
  process.exitCode = 1;
}

function isObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

function matchesType(v, t) {
  if (Array.isArray(t)) return t.some((x) => matchesType(v, x));
  switch (t) {
    case 'object':
      return isObject(v);
    case 'array':
      return Array.isArray(v);
    case 'string':
      return typeof v === 'string';
    case 'integer':
      return typeof v === 'number' && Number.isInteger(v);
    case 'number':
      return typeof v === 'number' && Number.isFinite(v);
    case 'boolean':
      return typeof v === 'boolean';
    case 'null':
      return v === null;
    default:
      return false;
  }
}

function validateFormat(value, format, pathStr, errors) {
  if (typeof value !== 'string') return;
  if (format === 'uri') {
    try {
      // eslint-disable-next-line no-new
      new URL(value);
    } catch {
      errors.push(`${pathStr}: expected URI format`);
    }
  } else if (format === 'uuid') {
    if (
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
        value,
      )
    ) {
      errors.push(`${pathStr}: expected uuid format`);
    }
  }
}

function validateSchema(data, schema, pathStr, errors, rootSchema) {
  rootSchema = rootSchema || schema;

  if (schema.const !== undefined && data !== schema.const) {
    errors.push(`${pathStr}: expected const ${JSON.stringify(schema.const)}`);
  }

  if (schema.enum && !schema.enum.includes(data)) {
    errors.push(`${pathStr}: value not in enum`);
  }

  if (schema.type !== undefined && !matchesType(data, schema.type)) {
    errors.push(
      `${pathStr}: expected type ${JSON.stringify(schema.type)}, got ${typeOf(data)}`,
    );
    return;
  }

  if (typeof data === 'string') {
    if (schema.minLength !== undefined && data.length < schema.minLength) {
      errors.push(`${pathStr}: string shorter than minLength ${schema.minLength}`);
    }
    if (schema.maxLength !== undefined && data.length > schema.maxLength) {
      errors.push(`${pathStr}: string longer than maxLength ${schema.maxLength}`);
    }
    if (schema.pattern) {
      const re = new RegExp(schema.pattern);
      if (!re.test(data)) {
        errors.push(`${pathStr}: does not match pattern ${schema.pattern}`);
      }
    }
    if (schema.format) validateFormat(data, schema.format, pathStr, errors);
  }

  if (typeof data === 'number') {
    if (schema.minimum !== undefined && data < schema.minimum) {
      errors.push(`${pathStr}: below minimum ${schema.minimum}`);
    }
    if (schema.maximum !== undefined && data > schema.maximum) {
      errors.push(`${pathStr}: above maximum ${schema.maximum}`);
    }
  }

  if (Array.isArray(data) && schema.items) {
    data.forEach((item, i) => {
      validateSchema(item, schema.items, `${pathStr}[${i}]`, errors, rootSchema);
    });
  }

  if (isObject(data) && schema.properties) {
    if (schema.required) {
      for (const key of schema.required) {
        if (!(key in data)) {
          errors.push(`${pathStr}: missing required property "${key}"`);
        }
      }
    }
    for (const [key, value] of Object.entries(data)) {
      if (schema.properties[key]) {
        validateSchema(
          value,
          schema.properties[key],
          `${pathStr}.${key}`,
          errors,
          rootSchema,
        );
      } else if (schema.additionalProperties === false) {
        errors.push(`${pathStr}: unexpected property "${key}"`);
      } else if (isObject(schema.additionalProperties)) {
        validateSchema(
          value,
          schema.additionalProperties,
          `${pathStr}.${key}`,
          errors,
          rootSchema,
        );
      }
    }
  }

  if (schema.anyOf) {
    const branchErrors = [];
    let ok = false;
    for (const branch of schema.anyOf) {
      const local = [];
      validateSchema(data, branch, pathStr, local, rootSchema);
      if (local.length === 0) {
        ok = true;
        break;
      }
      branchErrors.push(local);
    }
    if (!ok) {
      errors.push(
        `${pathStr}: failed anyOf (${branchErrors.map((e) => e.join('; ')).join(' | ')})`,
      );
    }
  }
}

function walkJsonFiles(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walkJsonFiles(p, out);
    else if (name.endsWith('.json')) out.push(p);
  }
  return out;
}

function main() {
  const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf8'));
  const files = walkJsonFiles(RECIPES_DIR);
  if (files.length === 0) {
    fail('no recipe JSON files found under recipes/');
    return;
  }

  const ids = new Map();
  let okCount = 0;

  for (const file of files) {
    const rel = path.relative(ROOT, file);
    let data;
    try {
      data = JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch (e) {
      fail(`${rel}: invalid JSON (${e.message})`);
      continue;
    }

    const errors = [];
    validateSchema(data, schema, '$', errors, schema);

    if (data && data.id) {
      if (ids.has(data.id)) {
        errors.push(`duplicate id "${data.id}" (also in ${ids.get(data.id)})`);
      } else {
        ids.set(data.id, rel);
      }
    }

    if (data && data.slug && !rel.includes(`${path.sep}${data.slug}${path.sep}`) && !rel.includes(`${path.sep}examples${path.sep}`)) {
      errors.push(
        `slug "${data.slug}" does not match parent directory for ${rel}`,
      );
    }

    if (data && data.verification && data.verification.status === 'example') {
      if (!rel.includes(`${path.sep}examples${path.sep}`)) {
        errors.push('status "example" only allowed under recipes/examples/');
      }
    } else if (
      data &&
      data.verification &&
      ['community', 'verified'].includes(data.verification.status)
    ) {
      if (!data.provenance || !data.provenance.source_url) {
        errors.push('community/verified recipes require provenance.source_url');
      }
    }

    if (errors.length) {
      fail(`${rel}:\n  - ${errors.join('\n  - ')}`);
    } else {
      okCount += 1;
      console.log('OK', rel);
    }
  }

  console.log(`Validated ${okCount}/${files.length} recipe file(s).`);
  if (process.exitCode) process.exit(1);
}

main();
