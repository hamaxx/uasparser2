import json
from uasparser import UASparser

up = UASparser()

uas_sample = {
	'Internet Explorer 7 (Windows Vista)' : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
	'Internet Explorer 6 (Windows XP)' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
	'Internet Explorer 5.5 (Windows 2000)' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )',
	'Internet Explorer 5.5 (Windows ME)' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)',
	'Firefox 3.0 (Windows XP)' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
	'Firefox 2.0 (Windows XP)' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14',
	'Google Chrome 0.2.149.29 (Windows XP)' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13',
	'Netscape 4.8 (Windows Vista)' : 'Mozilla/4.8 [en] (Windows NT 6.0; U)',
	'Netscape 4.8 (Windows XP)' : 'Mozilla/4.8 [en] (Windows NT 5.1; U)',
	'Opera 9.25 (Windows Vista)' : 'Opera/9.25 (Windows NT 6.0; U; en)',
	'Opera 8.0 (Windows 2000)' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; en) Opera 8.0',
	'Opera 7.51 (Windows XP)' : 'Opera/7.51 (Windows NT 5.1; U) [en]',
	'Opera 7.5 (Windows XP)' : 'Opera/7.50 (Windows XP; U)',
	'Avant Browser' : 'Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)',
	'Netscape 7.1 (Windows 98)' : 'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)',
	'Multizilla (Windows xp)' : 'Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a',
	'Opera 7.5 (Windows ME)' : 'Opera/7.50 (Windows ME; U) [en]',
	'Netscape 3.01 gold (Windows 95)' : 'Mozilla/3.01Gold (Win95; I)',
	'Netscape 2.02 (Windows 95)' : 'Mozilla/2.02E (Win95; U)',
	'Safari 125.8 (MacintoshOSX)' : 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.8',
	'Safari 85 (MacintoshOSX)' : 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/85.8',
	'MSIE 5.15 (MacintoshOS 9)' : 'Mozilla/4.0 (compatible; MSIE 5.15; Mac_PowerPC)',
	'Firefox 0.9 (MacintoshOSX )' : 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.7a) Gecko/20050614 Firefox/0.9.0+',
	'Omniweb563 (MacintoshOSX)' : 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US) AppleWebKit/125.4 (KHTML, like Gecko, Safari) OmniWeb/v563.15',
	'Mozilla 1.6 (Debian)' : 'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Debian/1.6-7',
	'Epiphany (Linux)' : 'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Epiphany/1.2.5',
	'Epiphany (Ubuntu)' : 'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.7.3) Gecko/20050924 Epiphany/1.4.4 (Ubuntu)',
	'Konqueror 3.5.10 (Kubuntu)' : 'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.10 (like Gecko) (Kubuntu)',
	'FireFox 2.0.0.19 (Ubuntu)' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) Gecko/20081216 Ubuntu/8.04 (hardy) Firefox/2.0.0.19',
	'Galeon 1.3.14 (Linux)' : 'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Galeon/1.3.14',
	'Konqueror 3 rc4 (Linux)' : 'Konqueror/3.0-rc4; (Konqueror/3.0-rc4; i686 Linux;;datecode)',
	'Konqueror (Gentoo)' : 'Mozilla/5.0 (compatible; Konqueror/3.3; Linux 2.6.8-gentoo-r3; X11;',
	'Firefox 0.8 (Linux)' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20050614 Firefox/0.8',
	'ELinks 0.9.3 (Kanotix)' : 'ELinks/0.9.3 (textmode; Linux 2.6.9-kanotix-8 i686; 127x41)',
	'Elinks (Linux)' : 'ELinks (0.4pre5; Linux 2.6.10-ac7 i686; 80x33)',
	'Links 2.1 (Linux)' : 'Links (2.1pre15; Linux 2.4.26 i686; 158x61)',
	'Links 0.9.1 (Linux)' : 'Links/0.9.1 (Linux 2.4.24; i386;)',
	'Opera 7.23 (Linux)' : 'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
	'Opera 9.52' : 'Opera/9.52 (X11; Linux i686; U; en)',
	'Lynx 2.8.5rel.1 (Linux)' : 'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/0.8.12',
	'w3m 0.5.1 (Linux)' : 'w3m/0.5.1',
	'Links 2 (FreeBSD)' : 'Links (2.1pre15; FreeBSD 5.3-RELEASE i386; 196x84)',
	'Mozilla 1.7 (FreeBSD)' : 'Mozilla/5.0 (X11; U; FreeBSD; i386; en-US; rv:1.7) Gecko',
	'Netscape 4.77 (Irix)' : 'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
	'Netscape 4.8 (SunOS)' : 'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)',
	'Net Positive (BeOS)' : 'Mozilla/3.0 (compatible; NetPositive/2.1.1; BeOS)',
	'Googlebot 2.1 (New version)' : 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
	'Googlebot 2.1 (Older Version)' : 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)',
	'Msnbot 1.0 (current version)' : 'msnbot/1.0 (+http://search.msn.com/msnbot.htm)',
	'Msnbot 0.11 (beta version)' : 'msnbot/0.11 (+http://search.msn.com/msnbot.htm)',
	'Yahoo Slurp' : 'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
	'Ask Jeeves/Teoma' : 'Mozilla/2.0 (compatible; Ask Jeeves/Teoma)',
	'scoutjet' : 'Mozilla/5.0 (compatible; ScoutJet; +http://www.scoutjet.com/)',
	'gulperbot' : 'Gulper Web Bot 0.2.4 (www.ecsl.cs.sunysb.edu/~maxim/cgi-bin/Link/GulperBot)',
	'Email Wolf' : 'EmailWolf 1.00',
	'grub client' : 'grub-client-1.5.3; (grub-client-1.5.3; Crawl your own stuff with http://grub.org)',
	'download demon' : 'Download Demon/3.5.0.11',
	'omni web' : 'OmniWeb/2.7-beta-3 OWF/1.0',
	'winHTTP' : 'SearchExpress',
	'ms url control' : 'Microsoft URL Control - 6.00.8862',
}

uas_obj = {}

for uas in uas_sample.values():
	uas_obj[uas] = up.parse(uas)

json.dump(uas_obj, open('uas.json', 'w'))
