import 'fight.dart';

class Event {
  final String id;
  final String name;
  final DateTime date;
  final String venue;
  final String location;
  final List<Fight> fights;
  final bool isUpcoming;
  final String? mainEventFightId;
  final String? imageUrl;
  final String status;

  Event({
    required this.id,
    required this.name,
    required this.date,
    required this.venue,
    required this.location,
    required this.fights,
    this.isUpcoming = true,
    this.mainEventFightId,
    this.imageUrl,
    this.status = 'scheduled',
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      venue: json['venue'] ?? '',
      location: json['location'] ?? '',
      fights: json['fights'] != null 
          ? (json['fights'] as List).map((fight) => Fight.fromJson(fight)).toList()
          : [],
      isUpcoming: json['is_upcoming'] ?? true,
      mainEventFightId: json['main_event_fight_id'],
      imageUrl: json['image_url'],
      status: json['status'] ?? 'scheduled',
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
      'is_upcoming': isUpcoming,
      'main_event_fight_id': mainEventFightId,
      'image_url': imageUrl,
      'status': status,
    };
  }

  Event copyWith({
    String? id,
    String? name,
    DateTime? date,
    String? venue,
    String? location,
    List<Fight>? fights,
    bool? isUpcoming,
    String? mainEventFightId,
    String? imageUrl,
    String? status,
  }) {
    return Event(
      id: id ?? this.id,
      name: name ?? this.name,
      date: date ?? this.date,
      venue: venue ?? this.venue,
      location: location ?? this.location,
      fights: fights ?? this.fights,
      isUpcoming: isUpcoming ?? this.isUpcoming,
      mainEventFightId: mainEventFightId ?? this.mainEventFightId,
      imageUrl: imageUrl ?? this.imageUrl,
      status: status ?? this.status,
    );
  }

  @override
  String toString() {
    return 'Event(id: $id, name: $name, date: $date, venue: $venue)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Event && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 