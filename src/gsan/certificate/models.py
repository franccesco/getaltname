"""ASN.1 models for parsing X.509 certificate Subject Alternative Names."""

from pyasn1.type import char, namedtype, tag, univ


class GeneralName(univ.Choice):
    """ASN.1 structure for a single Subject Alternative Name entry (DNS or IP)."""

    componentType = namedtype.NamedTypes(  # type: ignore[assignment]
        namedtype.NamedType(
            "dNSName",
            char.IA5String().subtype(  # type: ignore[attr-defined]
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2)
            ),
        ),
        namedtype.NamedType(
            "iPAddress",
            univ.OctetString().subtype(  # type: ignore[attr-defined]
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 7)
            ),
        ),
    )


class GeneralNames(univ.SequenceOf):
    """ASN.1 structure for a sequence of Subject Alternative Name entries."""

    componentType = GeneralName()  # type: ignore[assignment]
