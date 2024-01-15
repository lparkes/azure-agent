# $NetBSD$

DISTNAME=	2.9.1.1
PKGNAME=        azure-agent-${DISTNAME}
CATEGORIES=	sysutils python
MASTER_SITES=	${MASTER_SITE_GITHUB:=Azure/}
GITHUB_PROJECT=	WALinuxAgent
GITHUB_TAG=	v${PKGVERSION_NOREV}

MAINTAINER=	pkgsrc-users@NetBSD.org
HOMEPAGE=	https://github.com/Azure/WALinuxAgent
COMMENT=	Microsoft Azure Linux Agent
LICENSE=	apache-2.0

NO_BUILD=	yes
PLIST_SUBST+=	PYSITELIB=${PYSITELIB}
REPLACE_PYTHON=	bin/waagent bin/waagent2.0

SUBST_CLASSES+=		conf
SUBST_STAGE.conf=	pre-install
SUBST_FILES.conf=	azurelinuxagent/common/osutil/default.py
SUBST_FILES.conf+=	bin/waagent2.0

SUBST_SED.conf=		-e "s,@PKG_SYSCONFDIR@,${PKG_SYSCONFDIR},g"

EGDIR=		share/examples/${PKGBASE}
CONF_FILES+=	${EGDIR}/waagent.conf ${PKG_SYSCONFDIR}/waagent.conf

RCD_SCRIPTS=	waagent
FILES_SUBST+=	PYTHON=${PYTHONBIN:Q}
FILES_SUBST+=	PREFIX=${PREFIX}

INSTALLATION_DIRS=	sbin ${PYSITELIB} ${EGDIR}

pre-patch:
	${MKDIR} ${WRKSRC}/config/netbsd \
	    ${WRKSRC}/init/netbsd

post-install:
	${INSTALL_DATA} ${WRKSRC}/config/netbsd/waagent.conf	 \
	    "${DESTDIR}${PREFIX}/${EGDIR}/waagent.conf"

.include "../../lang/python/application.mk"
.include "../../lang/python/egg.mk"
.include "../../mk/bsd.pkg.mk"
