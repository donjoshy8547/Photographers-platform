def event_details(request):
    event_id = request.GET.get('id')
    if not event_id:
        messages.error(request, "No event specified")
        return redirect('/view_published_events')
    
    try:
        # Get the event details
        event = Events.objects.get(id=event_id)
        
        # Get assigned photographers if any
        assigned_photographers = []
        assignments = Assignassistance.objects.filter(evid=event)
        for assignment in assignments:
            if assignment.pid:
                assigned_photographers.append({
                    'name': assignment.pid.name,
                    'specialization': assignment.pid.specialization,
                    'location': assignment.pid.location
                })
            
            # Get assistant photographer details if assigned
            if assignment.asisst:
                try:
                    assistant = AsiPhotographrerReg.objects.get(id=assignment.asisst)
                    assigned_photographers.append({
                        'name': assistant.name,
                        'specialization': assistant.specialization,
                        'location': assistant.location,
                        'is_assistant': True
                    })
                except AsiPhotographrerReg.DoesNotExist:
                    pass
        
        # Get event applications if any
        applications = EventApplication.objects.filter(event=event)
        
        # Get related photos if any
        photos = Photo.objects.filter(eventid=event)
        
        context = {
            "event": event,
            "assigned_photographers": assigned_photographers,
            "applications": applications,
            "photos": photos
        }
        
        return render(request, "asphotograph/event_details.html", context)
    
    except Events.DoesNotExist:
        messages.error(request, "Event not found")
        return redirect('/view_published_events')
