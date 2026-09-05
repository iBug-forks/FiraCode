# iBug's README

## Build command

```sh
docker run -u 1000 -i --rm -v "${PWD}":/opt tonsky/firacode:latest ./script/build.sh --features cv02,cv10,cv16,cv29,ss01,ss03,ss05,zero --family-name "Fira Code iBug"
```

The selected variants are emitted under the required `rclt` OpenType feature,
not the optional `calt` feature used for Fira Code's programming ligatures.
They therefore remain active when an application turns off "Enable Ligatures".
The ligature setting still controls the programming ligatures themselves.

## Diff command

```sh
git diff -U0 --word-diff --no-index -- FiraCode.glyphs "Fira Code iBug.glyphs"
```
