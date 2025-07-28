import 'fight.dart';
import 'event.dart';

class FightCard {
  final String id;
  final String name;
  final DateTime date;
  final String venue;
  final String location;
  final List<Fight> fights;
  final bool isMainCard;
  final String? imageUrl;

  FightCard({
    required this.id,
    required this.name,
    required this.date,
    required this.venue,
    required this.location,
    required this.fights,
    this.isMainCard = false,
    this.imageUrl,
  });

  factory FightCard.fromJson(Map<String, dynamic> json) {
    return FightCard(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      venue: json['venue'] ?? '',
      location: json['location'] ?? '',
      fights: json['fights'] != null 
          ? (json['fights'] as List).map((fight) => Fight.fromJson(fight)).toList()
          : [],
      isMainCard: json['is_main_card'] ?? false,
      imageUrl: json['image_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'date': date.toIso8601String(),
      'venue': venue,
      'location': location,
      'fights': fights.map((fight) => fight.toJson()).toList(),
      'is_main_card': isMainCard,
      'image_url': imageUrl,
    };
  }

  FightCard copyWith({
    String? id,
    String? name,
    DateTime? date,
    String? venue,
    String? location,
    List<Fight>? fights,
    bool? isMainCard,
    String? imageUrl,
  }) {
    return FightCard(
      id: id ?? this.id,
      name: name ?? this.name,
      date: date ?? this.date,
      venue: venue ?? this.venue,
      location: location ?? this.location,
      fights: fights ?? this.fights,
      isMainCard: isMainCard ?? this.isMainCard,
      imageUrl: imageUrl ?? this.imageUrl,
    );
  }

  @override
  String toString() {
    return 'FightCard(id: $id, name: $name, date: $date, venue: $venue)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is FightCard && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 