import 'fight.dart';

class Event {
  final String id;
  final String title;
  final DateTime date;
  final String venue;
  final String location;
  final String type; // 'numbered', 'fight_night', etc.
  final String status; // 'scheduled' or 'completed'
  final String? eventUrl;

  Event({
    required this.id,
    required this.title,
    required this.date,
    required this.venue,
    required this.location,
    required this.type,
    required this.status,
    this.eventUrl,
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      id: json['id'] ?? '',
      title: json['name'] ?? '',  // Database uses 'name' instead of 'title'
      date: json['date'] != null ? DateTime.parse(json['date']) : DateTime.now(),
      venue: json['venue'] ?? '',
      location: json['location'] ?? '',
      type: json['type'] ?? 'numbered',
      status: json['status'] ?? 'scheduled',
      eventUrl: json['event_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'date': date.toIso8601String(),
      'venue': venue,
      'location': location,
      'type': type,
      'status': status,
      'event_url': eventUrl,
    };
  }

  @override
  String toString() {
    return 'Event(id: $id, title: $title, date: $date, venue: $venue, location: $location, type: $type, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Event && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 