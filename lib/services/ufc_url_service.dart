class UFCUrlService {
  // Mapping for fighters with special names that don't follow standard URL patterns
  static final Map<String, String> _nameMappings = {
    'Khabib Nurmagomedov': 'khabib-nurmagomedov',
    'Conor McGregor': 'conor-mcgregor',
    'Jon Jones': 'jon-jones',
    'Israel Adesanya': 'israel-adesanya',
    'Kamaru Usman': 'kamaru-usman',
    'Alexander Volkanovski': 'alexander-volkanovski',
    'Islam Makhachev': 'islam-makhachev',
    'Alexandre Pantoja': 'alexandre-pantoja',
  };

  /// Generates the base UFC athlete URL for a given fighter name
  static String generateFighterUrl(String fighterName) {
    // Check if we have a specific mapping first
    if (_nameMappings.containsKey(fighterName)) {
      return 'https://www.ufc.com/athlete/${_nameMappings[fighterName]}';
    }

    // Default URL generation logic
    String urlName = fighterName.toLowerCase()
        .replaceAll(' ', '-')
        .replaceAll('.', '')
        .replaceAll("'", '')
        .replaceAll('"', '')
        .replaceAll('(', '')
        .replaceAll(')', '')
        .replaceAll(',', '');
    
    // Handle special characters and accents
    urlName = urlName
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ñ', 'n')
        .replaceAll('ç', 'c');
    
    return 'https://www.ufc.com/athlete/$urlName';
  }

  /// Generates the UFC athlete stats/records URL for a given fighter name
  static String generateFighterStatsUrl(String fighterName) {
    return '${generateFighterUrl(fighterName)}#athlete-record';
  }

  /// Generates the UFC athlete rankings URL for a given fighter name
  static String generateFighterRankingsUrl(String fighterName) {
    return '${generateFighterUrl(fighterName)}#rankings';
  }
} 