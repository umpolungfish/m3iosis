use std::{env, fs, path::PathBuf};

fn main() {
    println!("cargo:rerun-if-env-changed=VOX_BAKED_INPUT_FILE");
    println!("cargo:rustc-link-arg-bin=factorization_31_resident=-nostartfiles");
    println!("cargo:rustc-link-arg-bin=phase_vessel_resident=-nostartfiles");
    let keys = ["VOX_PHASE_MODULUS_WORD", "VOX_PHASE_BASE_WORD", "VOX_PHASE_WIDTH_WORD"];
    let names = ["BAKED_MODULUS_WORD", "BAKED_BASE_WORD", "BAKED_WIDTH_WORD"];
    let file = env::var("VOX_BAKED_INPUT_FILE").ok().map(|path| {
        println!("cargo:rerun-if-changed={path}");
        fs::read_to_string(path).expect("read build-time IMASM input file")
    });
    let lines: Vec<_> = file.as_deref().map(|source| source.lines().collect()).unwrap_or_default();
    if file.is_some() {
        assert!((1..=4).contains(&lines.len()), "expected modulus and optional build words");
    }
    let mut generated = String::new();
    for (index, (key, name)) in keys.iter().zip(names).enumerate() {
        println!("cargo:rerun-if-env-changed={key}");
        let value = if file.is_some() { lines.get(index).map(|line| line.to_string()) } else { env::var(key).ok() };
        generated.push_str(&format!("#[allow(dead_code)]\nconst {name}: Option<&str> = {:?};\n", value.as_deref()));
    }
    let unit = lines.get(3).is_some_and(|marker| *marker == "unit");
    generated.push_str(&format!("#[allow(dead_code)]\nconst BAKED_BASE_IS_UNIT: bool = {unit};\n"));
    let factor_word = env::var("VOX_FACTOR_N_FILE").ok().map(|path| {
        println!("cargo:rerun-if-changed={path}");
        fs::read_to_string(path).expect("read baked IMASM factor numeral")
    });
    generated.push_str(&format!(
        "#[allow(dead_code)]\nconst FACTOR_N_WORD: Option<&str> = {:?};\n",
        factor_word.as_deref().map(str::trim_end)
    ));
    fs::write(PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("baked_inputs.rs"), generated)
        .expect("write generated membrane inputs");
}
