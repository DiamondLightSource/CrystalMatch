import setuptools

setuptools.setup(
    packages=[x for x in setuptools.find_packages() if x.startswith("CrystalMatch")],
)