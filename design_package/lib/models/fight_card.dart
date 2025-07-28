import 'event.dart';
import 'fight.dart';

class FightCard {
  final String id;
  final Event event;
  final List<Fight> mainCardFights;
  final List<Fight> prelimsFights;
  final List<Fight> earlyPrelimsFights;
  final DateTime lastScraped;
  final String dataSource; // 'espn', 'ufc.com', etc.
  final String? scrapedUrl;
  final bool isComplete; // Whether all fights have been scraped
  final String? notes;

  FightCard({
    required this.id,
    required this.event,
    this.mainCardFights = const [],
    this.prelimsFights = const [],
    this.earlyPrelimsFights = const [],
    required this.lastScraped,
    required this.dataSource,
    this.scrapedUrl,
    this.isComplete = false,
    this.notes,
  });

  factory FightCard.fromJson(Map<String, dynamic> json) {
    return FightCard(
      id: json['id'] ?? '',
      event: Event.fromJson(json['event'] ?? {}),
      mainCardFights: (json['main_card_fights'] as List<dynamic>?)
          ?.map((fight) => Fight.fromJson(fight))
          .toList() ?? [],
      prelimsFights: (json['prelims_fights'] as List<dynamic>?)
          ?.map((fight) => Fight.fromJson(fight))
          .toList() ?? [],
      earlyPrelimsFights: (json['early_prelims_fights'] as List<dynamic>?)
          ?.map((fight) => Fight.fromJson(fight))
          .toList() ?? [],
      lastScraped: json['last_scraped'] != null 
          ? DateTime.parse(json['last_scraped']) 
          : DateTime.now(),
      dataSource: json['data_source'] ?? '',
      scrapedUrl: json['scraped_url'],
      isComplete: json['is_complete'] ?? false,
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'event': event.toJson(),
      'main_card_fights': mainCardFights.map((fight) => fight.toJson()).toList(),
      'prelims_fights': prelimsFights.map((fight) => fight.toJson()).toList(),
      'early_prelims_fights': earlyPrelimsFights.map((fight) => fight.toJson()).toList(),
      'last_scraped': lastScraped.toIso8601String(),
      'data_source': dataSource,
      'scraped_url': scrapedUrl,
      'is_complete': isComplete,
      'notes': notes,
    };
  }

  // Get all fights combined
  List<Fight> get allFights => [
    ...mainCardFights,
    ...prelimsFights,
    ...earlyPrelimsFights,
  ];

  // Get total number of fights
  int get totalFights => allFights.length;

  // Get completed fights
  int get completedFights => allFights.where((fight) => fight.isCompleted).length;

  // Get upcoming fights
  int get upcomingFights => allFights.where((fight) => fight.isUpcoming).length;

  // Get cancelled fights
  int get cancelledFights => allFights.where((fight) => fight.isCancelled).length;

  // Get fights by card type
  List<Fight> getFightsByType(String cardType) {
    switch (cardType.toLowerCase()) {
      case 'main_card':
        return mainCardFights;
      case 'prelims':
        return prelimsFights;
      case 'early_prelims':
        return earlyPrelimsFights;
      default:
        return allFights;
    }
  }

  // Check if fight card has been updated recently
  bool get isRecentlyUpdated {
    final now = DateTime.now();
    final difference = now.difference(lastScraped);
    return difference.inHours < 24; // Updated within last 24 hours
  }

  // Get fight card summary
  String get summary {
    final total = totalFights;
    final completed = completedFights;
    final upcoming = upcomingFights;
    final cancelled = cancelledFights;
    
    return '$total total fights ($completed completed, $upcoming upcoming, $cancelled cancelled)';
  }

  // Get main event
  Fight? get mainEvent {
    if (mainCardFights.isNotEmpty) {
      return mainCardFights.first;
    }
    return null;
  }

  // Get co-main event
  Fight? get coMainEvent {
    if (mainCardFights.length > 1) {
      return mainCardFights[1];
    }
    return null;
  }

  // Check if this is a PPV event
  bool get isPPV {
    return event.title.toLowerCase().contains('ufc ') && 
           !event.title.toLowerCase().contains('fight night');
  }

  // Get broadcast information
  String get broadcastInfo {
    if (event.broadcastInfo != null) {
      return event.broadcastInfo!;
    }
    
    if (isPPV) {
      return 'Pay-Per-View';
    }
    
    return 'ESPN/ESPN+';
  }
} 