//! phase_unbraider — IMASM-resident phase readout, the Vox membrane.
//!
//! Three surfaces of the same instrument, baked as IMASM numeral words:
//!
//!   surface A — QFT-register phase readout (PRIMARY, this bin):
//!     `phase_unbraid::run_phase_unbraid(n_val, a, max_shots)`. The index
//!     register holds the post-modexp collapsed comb, the exact QFT unitary
//!     is applied (radix-2 FFT, O(M log M)), ONE k is measured from the
//!     Born distribution, the winding k/M is continued-fractioned into
//!     s/r0, the period r is lifted by powm, and the factors close via one
//!     gcd. Caps at M = 2^27 ≈ 134M amplitudes → N up to ~2^63.
//!
//!   surface B — braid-filtration phase readout (tape register):
//!     Same algorithm in the tape register. `shor_braid::shor_factor_via_braid`
//!     emits the braid word W = W_Shor(a, N), reads r = ord_N(a) via
//!     `winding_number_tape(W)`, closes via one gcd. Works on arbitrary
//!     widths but the per-base orbit walk is O(r) tape ops; on huge-ord N
//!     the walk is bounded by a cap.
//!
//!   surface C — Vox resident-sidearm membrane (shor_qft::run_shor_big_report):
//!     Fermet close → smart_factor wide (Pollard rho + MPQS + Dixon) → braid
//!     filtration → symbolic filtration. The same (a, n) bake shape.
//!
//! Routing: surface A when N fits u64, surface B otherwise. Surface C as a
//! classical fall-through.
//!
//! Every operand is a baked IMASM numeral word; the runtime is pure dispatch.
//! μ∘δ = id: encode(N) emits the word, bake binds it, run consumes it.
//!
//! Build (mirrors factor_one.sh / membrane_one.sh exactly):
//!   cargo build --release --bin vox
//!   NWORD="$(./target/release/vox numeral <N>)"
//!   AWORD="$(./target/release/vox numeral 2)"
//!   MEMBRANE_WORDS="$AWORD $NWORD" cargo build --release --bin phase_unbraider
//!   ./target/release/phase_unbraider

extern crate alloc;
#[path = "../phase_unbraid.rs"] mod phase_unbraid;

mod native_numeral {
    use num_bigint::BigUint;
    use vox::morphism_factor::{cmp, decimal_to_tape, dec_of, emit_numeral, mul, parse_numeral};

    pub fn decode(value: &str) -> Option<BigUint> {
        let tape = parse_numeral(value).ok()?;
        BigUint::parse_bytes(dec_of(&tape).as_bytes(), 10)
    }

    pub fn encode(value: &str) -> String {
        let tape = decimal_to_tape(value).or_else(|| parse_numeral(value).ok())
            .expect("decimal or IMASM numeral");
        emit_numeral(&tape)
    }

    pub fn multiply_via_word(p: &BigUint, q: &BigUint) -> BigUint {
        let p = decimal_to_tape(&p.to_str_radix(10)).expect("positive factor");
        let q = decimal_to_tape(&q.to_str_radix(10)).expect("positive factor");
        BigUint::parse_bytes(dec_of(&mul(&p, &q)).as_bytes(), 10).expect("product numeral")
    }

    pub fn syzygy_preserves(source: &BigUint, p: &BigUint, q: &BigUint) -> bool {
        let Some(source) = decimal_to_tape(&source.to_str_radix(10)) else { return false };
        let Some(p) = decimal_to_tape(&p.to_str_radix(10)) else { return false };
        let Some(q) = decimal_to_tape(&q.to_str_radix(10)) else { return false };
        cmp(&mul(&p, &q), &source).is_eq()
    }

    pub fn factor_words_line(p: &BigUint, q: &BigUint) -> String {
        let p = decimal_to_tape(&p.to_str_radix(10)).expect("positive factor");
        let q = decimal_to_tape(&q.to_str_radix(10)).expect("positive factor");
        format!("p_word {}\nq_word {}\n", emit_numeral(&p), emit_numeral(&q))
    }
}

fn main() {
    ::vox::ordering::cli::intercept();
    let result = (|| -> Result<String, String> {
        let raw = option_env!("MEMBRANE_WORDS")
            .ok_or("Build with MEMBRANE_WORDS=\"<a-word> <N-word>\"")?;
        let mut words: Vec<Vec<char>> = Vec::new();
        for w in raw.split_whitespace() {
            words.push(::vox::morphism_factor::parse_numeral(w)
                .map_err(|e| format!("numeral parse: {e}"))?);
        }
        if words.len() != 2 { return Err("phase_unbraider needs a and N (two words)".into()); }
        let a_tape = &words[0];
        let n_tape = &words[1];

        // Decode N as u64 (surface A works on the u64 register).
        let n_dec = ::vox::morphism_factor::dec_of(n_tape);
        let n_val: u64 = n_dec.parse().map_err(|_| "N does not fit u64; surface A caps there")?;
        let a_val: u64 = ::vox::morphism_factor::dec_of(a_tape).parse()
            .map_err(|_| "a does not fit u64")?;

        let mut o = String::new();
        o.push_str("phase_unbraider — factors from a phase readout, no search\n");
        o.push_str("surface A: QFT-register phase readout (phase_unbraid)\n");
        o.push_str(&alloc::format!("N = {}  ({}-bit u64 register; M = 2^q with q chosen so M >= N^2)\n", n_dec, u64::BITS - n_val.leading_zeros()));
        o.push_str(&alloc::format!("a = {}\n", a_val));

        let report = phase_unbraid::phase_unbraid_report(&n_dec, a_val, 64)?;
        o.push_str(&report);
        Ok(o)
    })();
    match result {
        Ok(report) => println!("{report}"),
        Err(error) => { eprintln!("{error}"); std::process::exit(2); }
    }
}
