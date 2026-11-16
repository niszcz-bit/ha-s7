# Siemens S7 PLC Plus — persönlicher Fork

> **Hinweis in aller Deutlichkeit:** Dieses Repository ist **nicht böse gemeint**
> und richtet sich gegen niemanden. Es ist ein **privater Fork** von
> [gijzelaerr/ha-s7](https://github.com/gijzelaerr/ha-s7) — einer großartigen
> Integration, bei der die gesamte Arbeit und das Verdienst beim
> **Originalautor** liegen.
>
> Ich habe lediglich zwei Kleinigkeiten ergänzt, **die ich selbst zu Hause
> gebraucht habe**, und stelle sie hier öffentlich bereit, damit ich sie
> bequem über HACS in mein eigenes Home Assistant ziehen kann. Kein
> kommerzielles Interesse, keine Konkurrenz, keine Kritik am Original.

## Was dieser Fork anders macht

- **Eigene Domain `s7_plus`** („Siemens S7 PLC Plus"), damit er sich
  parallel zur Original-Integration installieren lässt, ohne Konflikte.
- **Eigene Namen pro Tag:** `DB1.DBD0:REAL = Vorlauftemperatur`
  benennt die Entität; die interne ID bleibt an der Adresse.
- **Push-Taster statt Toggle-Schalter:** `M10.0:BOOL = Licht EIN | push`
  (oder `| push:1.0` für die Dauer in Sekunden) erzeugt einen Taster, der
  das Bit kurz setzt und automatisch wieder zurücknimmt — für SPS-Programme
  mit getrennten Ein-/Aus-Bits.

## Beispiel-Tagliste

```
DB1.DBX6.0:BOOL = Wohnzimmer Licht EIN | push
DB1.DBX6.1:BOOL = Wohnzimmer Licht AUS | push
DB1.DBD0:REAL = Vorlauftemperatur
```

## Dienste

`s7_plus.write_tag` und `s7_plus.pulse_tag` (statt `s7.*` im Original).

## Lizenz & Dank

MIT — siehe [LICENSE](LICENSE). Danke an
[@gijzelaerr](https://github.com/gijzelaerr) für die Original-Integration.
Fehler und Eigenheiten dieses Forks gehen auf mich, nicht auf das Original.
