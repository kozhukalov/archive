## Hiera configuration ##

By default hiera looks up config its config file `hiera.yaml` in
`/etc/puppetlabs/code` directory. Here is a minimal example of Hiera
configuration file.

```yaml
---
  !ruby/sym logger: noop
  !ruby/sym backends:
    - yaml
  !ruby/sym yaml:
    !ruby/sym datadir: /etc/hiera
  !ruby/sym hierarchy:
    - provision
```

One can take a look at
Hiera [documentation](https://docs.puppet.com/hiera/3.3/configuring.html) for
detailed explanaition of the structure of `hiera.yaml`

```bash
mkdir -p /etc/puppetlabs/code
cp hiera.yaml /etc/hiera.yaml
ln -s /etc/hiera.yaml /etc/puppetlabs/code/hiera.yaml
```

## Hiera data ##

In the `hiera.yaml` file hiera data directory is set to `/etc/hiera` which means
we need to put (manually or using any automatic serializer) the file
`provision.yaml` to this data directory.

```bash
mkdir -p /etc/hiera
cp provision.yaml /etc/hiera/provision.yaml
```
