Instance Switcher
=================

Simple python script to change the machine equivalent /etc/hosts to each and every ELB instance.

virtualenvwrapper friendly.

Work in progress.


# TL;DR

```
git clone http://github.com/davividal/instanceswitcher && cd instanceswitcher
pip install -r requirements.txt
cat <<EOF | sudo tee /etc/sudoers.d/instanceswitcher
$USERNAME  ALL=(ALL) NOPASSWD: $PWD/puppet/puppet_wrapper.sh
EOF
python switch.py
```

# How to use

1. Clone this repo
	```
	$ git clone http://github.com/davividal/instanceswitcher && cd instanceswitcher
	```
1. Install its dependencies
	```
	$ pip install -r requirements.txt
	```

1. Add to your sudoers:
	```bash
	cat <<EOF | sudo tee /etc/sudoers.d/instanceswitcher
	$USERNAME  ALL=(ALL) NOPASSWD: $PWD/puppet/puppet_wrapper.sh
	EOF
	```

1. Execute it:
	```
	$ python switch.py
	```
