# iBug's README

## Build command

```sh
docker run -u 1000 -i --rm -v "${PWD}":/opt tonsky/firacode:latest ./script/build.sh -f cv02,cv10,cv16,cv29,ss01,ss03,ss05,zero -n "Fira Code iBug"
```

## Diff command

```sh
git diff -U0 --word-diff --no-index -- FiraCode.glyphs "Fira Code iBug.glyphs"
```
