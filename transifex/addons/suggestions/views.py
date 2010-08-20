# -*- coding: utf-8 -*-
from django.http import (HttpResponse, HttpResponseBadRequest)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from models import Suggestion
from languages.models import Language
#from projects.models import Project
#from projects.permissions import *
#from projects.permissions.project import ProjectPermission
from resources.models import SourceEntity
#from txcommon.decorators import one_perm_required_or_403


# FIXME: Permission checking
# Restrict access only for private projects since this is used to fetch stuff
# Allow even anonymous access on public projects
def entity_suggestions_snippet(request, entity_id, lang_code):
    """Return an HTML snippet with translation suggestions.
    
    We're also passing current_translation to be able to show a "tick" next
    to the one suggestion which is active.
    
    This view is specific to Transifex and Lotte.
    """

    source_entity = get_object_or_404(SourceEntity, pk=entity_id)
    current_translation = source_entity.get_translation(lang_code)
    suggestions = source_entity.suggestions.filter(language__code=lang_code).order_by('-score')
    #FIXME: Should only pass to the template the ID of the active suggestion:
    #enabled_suggestion = suggestions.filter(string=current_translation.string)

    return render_to_response("lotte_suggestions_snippet.html", {
        'suggestions': suggestions,
        'source_entity': source_entity,
        'lang_code': lang_code,
        'current_translation': current_translation},
    context_instance = RequestContext(request))


#FIXME: Full permission checking
#FIXME: Get this into Piston instead, as part of the normal API.
def entity_suggestion_create(request, entity_id, lang_code):
    """Create a suggestion for an entity and a language."""

    #FIXME: All basic POST checks could be done in a decorator.
    if not request.method == "POST":
        return HttpResponseBadRequest("POST method only allowed.")
    suggestion_string = request.POST['suggestion_string']
    if not suggestion_string:
        return HttpResponseBadRequest("POST variable 'suggestion_string' missing.")

    source_entity = get_object_or_404(SourceEntity, pk=entity_id)
    language = Language.objects.by_code_or_alias(lang_code)
    source_entity.suggestions.create(language=language,
                                     string=request.POST['suggestion_string'],
                                     user=request.user)
    return HttpResponse(status=200)


#FIXME: Full permission checking
#FIXME: Get this into Piston instead, as part of the normal API.
def entity_suggestion_vote(request, entity_id, lang_code, suggestion_id, direction):
    """Vote up or down for a suggestion."""

    #FIXME: All basic POST checks could be done in a decorator.
    if not request.method == "POST":
        return HttpResponseBadRequest("POST method only allowed.")
        
    suggestion = get_object_or_404(Suggestion, pk=suggestion_id)

    if direction == 'up':
        suggestion.vote_up(request.user)
    elif direction == 'down':
        suggestion.vote_down(request.user)
    
    return HttpResponse(status=200)
