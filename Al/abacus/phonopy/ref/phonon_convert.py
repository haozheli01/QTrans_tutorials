#!/usr/bin/env python3
# Provided by QTrans.
# Updated: 2026-11-11
"""Convert Phonopy type-1 FORCE_SETS to the units expected by QTrans.

ABACUS: displacements in bohr -> angstrom; forces remain in eV/angstrom.
VASP:   displacements and forces already use angstrom and eV/angstrom.

Run this on the original FORCE_SETS, never on an already converted file.
The input is preserved, and an existing output is not overwritten.
"""

import argparse
from pathlib import Path

import numpy as np
from phonopy.file_IO import get_FORCE_SETS_lines, parse_FORCE_SETS
from phonopy.interface.calculator import get_default_physical_units


def convert_force_sets(input_path: Path, output_path: Path, calculator: str) -> None:
    """Validate and convert a finite-displacement (type-1) force dataset."""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output must be different files.")
    if output_path.exists():
        raise FileExistsError(f"Output already exists: {output_path}")

    # FORCE_SETS does not record its source units. The caller must select
    # the interface that produced the original, unconverted file.
    dataset = parse_FORCE_SETS(filename=str(input_path))
    if not dataset or "first_atoms" not in dataset:
        raise ValueError("Expected a Phonopy type-1 FORCE_SETS file.")
    natoms = int(dataset["natom"])
    if natoms <= 0 or not dataset["first_atoms"]:
        raise ValueError("The dataset must contain atoms and displacements.")

    # Use the installed Phonopy convention rather than a rounded conversion
    # factor. Both supported interfaces supply forces in eV/angstrom.
    units = get_default_physical_units(calculator)
    displacement_factor = units["distance_to_A"]
    for index, entry in enumerate(dataset["first_atoms"], start=1):
        displacement = np.asarray(entry["displacement"], dtype=float)
        forces = np.asarray(entry["forces"], dtype=float)
        if displacement.shape != (3,) or forces.shape != (natoms, 3):
            raise ValueError(f"Invalid array shape in displacement {index}.")
        if not np.isfinite(displacement).all() or not np.isfinite(forces).all():
            raise ValueError(f"Nonfinite values in displacement {index}.")
        if not 0 <= int(entry["number"]) < natoms:
            raise ValueError(f"Invalid displaced atom in displacement {index}.")
        entry["displacement"] = displacement * displacement_factor
        entry["forces"] = forces  # Already in eV/angstrom; do not rescale.

    # Exclusive creation protects existing reference data from accidental
    # replacement. Phonopy writes the validated dataset in its usual format.
    with output_path.open("x", encoding="utf-8") as output:
        output.write("\n".join(get_FORCE_SETS_lines(dataset)) + "\n")
    print(f"Wrote {output_path}: {natoms} atoms, "
          f"{len(dataset['first_atoms'])} displacement(s).")
    print(f"Displacement factor: {displacement_factor:.15g}; force factor: 1.")
    print("Output units: angstrom and eV/angstrom.")


def main() -> None:
    """Read command-line options and report conversion errors clearly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calculator", choices=("abacus", "vasp"), default="abacus",
                        help="Phonopy interface used for the original file (default: abacus).")
    parser.add_argument("--input", type=Path, default=Path("FORCE_SETS"),
                        help="Original type-1 dataset (default: FORCE_SETS).")
    parser.add_argument("--output", type=Path, default=Path("FORCE_SETS_converted"),
                        help="New file in QTrans units (default: FORCE_SETS_converted).")
    args = parser.parse_args()
    try:
        convert_force_sets(args.input, args.output, args.calculator)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        parser.exit(1, f"Conversion failed: {error}\n")


if __name__ == "__main__":
    main()
