(* Basic types *)
Parameter Entity : Type.
Parameter Event : Type.

Parameter Rel : Entity -> Entity -> Prop.
Parameter Mod : Entity -> Event -> Prop.
Parameter Prog : Prop -> Prop.
Parameter this : (Entity -> Prop) -> Entity.
Parameter that : (Entity -> Prop) -> Entity.

(* Temporal operators *)
Parameter Hold : Event -> Prop.
Parameter Cul : Event -> Prop.
Parameter Past : Event -> Prop.
Parameter Future : Event -> Prop.

(* Modal operators *)
Parameter Poss : Event -> Prop.
Parameter NonPoss : Event -> Prop.

(* Proposition marker and question marker *)
Parameter Content : Entity -> (((Event -> Prop) -> Event -> Prop) -> Prop) -> Prop.
Parameter WH : Prop -> Prop.

(* Thematic roles *)
Parameter Subj : Event -> Entity.
Parameter Top : Event -> Entity.
Parameter Nom : Event -> Entity.
Parameter Acc : Event -> Entity.
Parameter AccI : Event -> Prop -> Prop.
Parameter AccE : Event -> Event.
Parameter Dat : Event -> Entity.
Parameter Attr : Event -> Entity.
Parameter Deg : Event -> Entity.

(* My roles *)
Parameter asEntity : Event -> Entity.
Parameter PartOf : Entity -> Entity -> Prop.
Parameter Of : Entity -> Entity -> Prop.
Parameter _する : Event -> Prop.
Parameter Obj : Entity -> Event.
Parameter _アシドxmdashxシス : Entity -> Prop.
Parameter _こと : Entity -> Prop.
Parameter _ドレナxmdashxジ術 : Entity -> Prop.
Parameter _アプロxmdashxチ : Event -> Prop.
Parameter _ドレxmdashxン : Entity -> Prop.
Parameter _コントロxmdashxル : Event -> Prop.
Parameter K_e3 : (Event -> Prop) -> (Event -> Prop).
Parameter K_4 : (Event -> Prop) -> (Event -> Prop).
Parameter _尿道カテxmdashxテル : Entity -> Prop.
Parameter _プレイルxmdashxム内 : Entity -> Prop.
Parameter _アルコxmdashxル性 : Entity -> Prop.

(* Binary quantifiers *)
Parameter Most : (Entity -> Prop) -> (Entity -> Prop) -> Prop.

(* Notation "'most' x ; P , Q" := (Most (fun x => P) (fun x => Q))
   (at level 30, x ident, right associativity) : type_scope. *)

Axiom most_ex_import :
  forall (F G: Entity -> Prop),
   (Most F G -> exists x, F x /\ G x).

Axiom most_consv :
  forall (F G: Entity -> Prop),
   (Most F G -> Most F (fun x => (F x /\ G x))).

Axiom most_rightup :
  forall (F G H: Entity -> Prop),
   ((Most F G) ->
   (forall x, G x -> H x) -> (Most F H)).

(* Unary quantifiers *)
Parameter Few : (Entity -> Prop) -> Prop.

Axiom few_down :
  forall (F G: Entity -> Prop),
   Few F -> (forall x, G x -> F x) -> Few G.

(* Veridical predicates *)
Parameter _たしか : Event -> Prop.
Axiom factive_たしか1 : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  _たしか v -> Content (Nom v) P -> P (fun I => I).
Axiom factive_たしか2 : forall v : Event, forall P : Prop,
  _たしか v -> AccI v P ->  P.
Ltac solve_たしか :=
 match goal with
   | [H1 : _たしか ?e, H2 : Content (Nom ?e) _ |- _] => try apply factive_たしか1 with (v:=e) in H2
   | [H1 : _たしか ?e, H2 : AccI ?e _ |- _] => try apply factive_たしか2 with (v := e) in H2
 end.

Parameter _本当 : Entity -> Prop.
Axiom factive_本当 : forall v : Event, forall P : Prop,
  _本当 (Nom v) -> AccI v P -> P.
Ltac solve_本当 :=
 match goal with
   H1 : _本当 (Nom ?e), H2 : AccI ?e _ |- _
     => try apply factive_本当 with (v := e) in H2
 end.

(* Anti-veridical predicates *)
Parameter _嘘 : Entity -> Prop.
Axiom factive_嘘 : forall v : Event, forall P : Prop,
  _嘘 (Nom v) -> AccI v P -> ~P.

Ltac solve_嘘 :=
 match goal with
   H1 : _嘘 (Nom ?e), H2 : AccI ?e _ |- _
     => try apply factive_嘘 with (v := e) in H2
 end.

Axiom anti_factive_NonPoss1 : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  NonPoss v -> Content (Nom v) P -> ~ (P (fun I => I)).
Axiom anti_factive_NonPoss2 : forall v : Event, forall P : Prop,
  NonPoss v -> AccI v P -> ~P.

Ltac solve_Poss :=
 match goal with
   | [H1 : NonPoss ?e, H2 : Content (Nom ?e) _ |- _] => try apply anti_factive_NonPoss1 with (v:=e) in H2
   | [H1 : NonPoss ?e, H2 : AccI ?e _ |- _] => try apply anti_factive_NonPoss2 with (v := e) in H2
 end.

(* Attitude verbs *)
Parameter _疑う : Event -> Prop.
Parameter _思う : Event -> Prop.
Axiom pos_疑う_思う : forall (v : Event) (P : Prop), (_疑う v -> AccI v P -> _思う v /\ AccI v P).
Axiom neg_prop_疑う_思う : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  _疑う v -> Content (Acc v) P -> _思う v /\ AccI v (~ (P (fun I => I))).
Axiom neg_wh_疑う_思う : forall v P, (_疑う v -> AccI v (WH (~P)) -> _思う v /\ AccI v P).

Ltac solve_疑う_思う :=
 match goal with
   | [H1 : _疑う ?e, H2 : AccI ?e (WH _) |- _] => try apply neg_wh_疑う_思う with (v := e) in H2
   | [H1 : _疑う ?e, H2 : Content (Acc ?e) _ |- _] => try apply neg_prop_疑う_思う with (v:=e) in H2
   | [H1 : _疑う ?e, H2 : AccI ?e _ |- _] => try apply pos_疑う_思う with (v := e) in H2
 end.

(* Implicative verbs *)
Parameter _成功 : Event -> Prop.
Axiom implicative_成功 : forall (v : Event) (x : Entity) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  _成功 v -> Nom v = x -> Past v -> Content (Dat v) P -> P (fun J : Event -> Prop => fun e : Event => J e /\ Nom e = x /\ Past e).
Ltac solve_成功 :=
 match goal with
   | [H1 : _成功 ?e, H2 : Nom ?e = ?t, H3 : Past ?e, H4 : Content (Dat ?e) _ |- _]
     => apply implicative_成功 with (v:=e)(x:=t) in H4
 end.

(* Perceptual verbs *)
Parameter _見る : Event -> Prop.
Axiom factive_見る : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  _見る v -> Past v -> Content (Acc v) P -> P (fun J : Event -> Prop => fun e : Event => J e /\ Past e).
Ltac solve_factive_見る :=
 match goal with
   | [H1 : _見る ?e, H2 : Past ?e, H3 : Content (Acc ?e) _ |- _]
     => apply factive_見る with (v:=e) in H3
 end.

Axiom closure_見る : forall (v: Event) (P P': ((Event -> Prop) -> Event -> Prop) -> Prop),
  _見る v -> Content (Acc v) P -> (P (fun I => I) -> P' (fun I => I)) -> Content (Acc v) P'.
Ltac solve_closure_見る :=
 match goal with
   | [H1 : _見る ?e, H2 : Content (Acc ?e) ?A |- Content (Acc ?e) ?B ]
     => apply closure_見る with (v:=e)(P:=A)(P':=B)
 end.

Parameter _聞く : Event -> Prop.
Axiom factive_聞く : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  _聞く v -> Past v -> Content (Acc v) P -> P (fun J : Event -> Prop => fun e : Event => J e /\ Past e).
Ltac solve_factive_聞く :=
 match goal with
   | [H1 : _聞く ?e, H2 : Past ?e, H3 : Content (Acc ?e) _ |- _]
     => apply factive_聞く with (v:=e) in H3
 end.

Axiom closure_聞く : forall (v: Event) (P P': ((Event -> Prop) -> Event -> Prop) -> Prop),
  _聞く v -> Content (Acc v) P -> (P (fun I => I) -> P' (fun I => I)) -> Content (Acc v) P'.
Ltac solve_closure_聞く :=
 match goal with
   | [H1 : _聞く ?e, H2 : Content (Acc ?e) ?A |- Content (Acc ?e) ?B ]
     => apply closure_聞く with (v:=e)(P:=A)(P':=B)
 end.

(* privative adjectives *)
Parameter _former : (Entity -> Prop) -> Entity -> Prop.
Axiom privative_former : forall F : Entity -> Prop, forall x : Entity, (_former F x -> ~ (F x)).
Ltac solve_privative_former :=
  match goal with
    H : _former ?A ?t |- _
    => try apply privative_former with (F:= A)(x:= t) in H
  end.

Parameter _fake : (Entity -> Prop) -> Entity -> Prop.
Axiom privative_fake : forall F : Entity -> Prop, forall x : Entity, (_fake F x -> ~ (F x)).
Ltac solve_privative_fake :=
  match goal with
    H : _fake ?A ?t |- _
    => try apply privative_fake with (F:= A)(x:= t) in H
  end.

Parameter _一流 : (Entity -> Prop) -> Entity -> Prop.

Parameter _自称 : (Entity -> Prop) -> Entity -> Prop.
Axiom wouldbe : forall F G: Entity -> Prop, forall x : Entity, _自称 F x -> (F x -> G x) -> _自称 G x.
Ltac solve_closure_wouldbe :=
  match goal with
    H : _自称 ?A ?t |- _自称 _ _
    => try apply wouldbe with (F:= A); try apply H
  end.

(* intensional verbal modifiers *)
Parameter _ほぼ : (Event -> Prop) -> Event -> Prop.
Axiom anti_veridical_ほぼ : forall F : Event -> Prop, forall v : Event, (_ほぼ F v -> ~ (F v)).
Ltac solve_anti_veridical_ほぼ :=
  match goal with
    H : _ほぼ ?A ?t |- _
    => try apply anti_veridical_ほぼ with (F:= A)(v:= t) in H
  end.

Parameter _損ねる : (Event -> Prop) -> Event -> Prop.
Axiom anti_veridical_損ねる : forall F : Event -> Prop, forall v : Event, (_損ねる F v -> ~ (F v)).
Ltac solve_anti_veridical_損ねる :=
  match goal with
    H : _損ねる ?A ?t |- _
    => try apply anti_veridical_損ねる with (F:= A)(v:= t) in H
  end.

(* antonyms *)
Parameter _大きな : Entity -> Prop.
Parameter _小さな : Entity -> Prop.
Axiom antonym_大きな_小さな : forall x : Entity, _大きな x -> _小さな x -> False.
Ltac solve_antonym_大きな_小さな :=
  match goal with
    H1 : _大きな _, H2 : _小さな ?t |- False
  => try apply antonym_大きな_小さな with (x := t)
  end.

Parameter _おいしい : Event -> Prop.
Parameter _まずい : Event -> Prop.
Axiom antonym_おいしい_まずい : forall v : Event, _おいしい v -> _まずい v -> False.
Ltac solve_antonym_おいしい_まずい :=
  match goal with
    H1 : _おいしい _, H2 : _まずい ?e |- False
  => try apply antonym_おいしい_まずい with (v := e)
  end.

Parameter _開く : Event -> Prop.
Parameter _閉まる : Event -> Prop.
Axiom antonym_開く_閉まる : forall v : Event, _開く v -> _閉まる v -> False.
Ltac solve_antonym_開く_閉まる :=
  match goal with
    H1 : _開く ?e, H2 : _閉まる ?e |- _
  => try apply antonym_開く_閉まる with (v := e) in H1
  end.

(* causatives and benefactives *)
Parameter _せる : Event -> Prop.
Parameter _もらう : Event -> Prop.

Axiom causative1 : forall v : Event, forall x : Entity,
  _せる v -> Dat v = x -> Nom v = x.
Axiom causative2 : forall v : Event, forall x : Entity,
  _せる v -> Acc v = x -> Nom v = x.
Hint Resolve causative1 causative2.

Axiom benefactive : forall v : Event, forall x : Entity,
  _もらう v -> Dat v = x -> Nom v = x.
Hint Resolve benefactive.


(* Causative alternation *)
Parameter _破く : Event -> Prop.
Parameter _破れる : Event -> Prop.
Axiom causative_破く_破れる : forall v : Event,
  _破く v -> _破れる v /\ Nom v = Acc v.

Ltac solve_causative_破く_破れる :=
  match goal with
    | [ H1 : _破く ?e |- _ ]
     => apply causative_破く_破れる with (v := e) in H1
  end.

Parameter _閉める : Event -> Prop.
Axiom causative_閉める_閉まる : forall v : Event,
  _閉める v -> _閉まる v /\ Nom v = Acc v.

Ltac solve_causative_閉める_閉まる :=
  match goal with
    | [ H1 : _閉める ?e |- _ ]
     => apply causative_閉める_閉まる with (v := e) in H1
  end.

(* My role *)
Axiom factive_AccI : forall v : Event, forall P : Prop,
  P -> AccI v P.
Axiom factive_AccI2 : forall v : Event, forall P : Prop,
  AccI v P ->  P.

Parameter _なる : Event -> Prop.
Parameter _診断 : Event -> Prop.
Parameter _考える : Event -> Prop.

Ltac solve_factive_AccI :=
 match goal with
   | [H1 : _なる ?e |- AccI ?e _] => apply factive_AccI with (v := e)
   | [H1 : _する ?e |- AccI ?e _] => apply factive_AccI with (v := e)
   | [H1 : _診断 ?e |- AccI ?e _] => apply factive_AccI with (v := e)
   | [H1 : _考える ?e |- AccI ?e _] => apply factive_AccI with (v := e)
   | [H1 : _なる ?e, H2 : AccI ?e _ |- _] => apply factive_AccI2 with (v := e) in H2
   | [H1 : _する ?e, H2 : AccI ?e _ |- _] => apply factive_AccI2 with (v := e) in H2
   | [H1 : _診断 ?e, H2 : AccI ?e _ |- _] => apply factive_AccI2 with (v := e) in H2
   | [H1 : _考える ?e, H2 : AccI ?e _ |- _] => apply factive_AccI2 with (v := e) in H2
 end.

Axiom factive_Content : forall (x : Entity) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  Content x P -> P (fun I => I).
Axiom factive_Content3 : forall (x : Entity) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  P (fun I => I) -> Content x P.

Parameter _ところ : Entity -> Prop.
Parameter _ため : Entity -> Prop.

Ltac solve_Content :=
  match goal with
    | [H1 : _ところ ?e, H2 : Content ?e _ |- _] => try apply factive_Content with (x:=e) in H2
    | [H1 : _ため ?e, H2 : Content ?e _ |- _] => try apply factive_Content with (x:=e) in H2
    | [H1 : _ところ ?e |- Content ?e _] => try apply factive_Content3 with (x:=e)
    | [H1 : _ため ?e |- Content ?e _] => try apply factive_Content3 with (x:=e)
  end.

Parameter _認める : Event -> Prop.
Axiom factive_Content2 : forall (v : Event) (P : ((Event -> Prop) -> Event -> Prop) -> Prop),
  Content (Acc v) P -> P (fun I => I).
Ltac solve_Content2 :=
  match goal with
    | [H1 : _認める ?e, H2 : Content (Acc ?e) _ |- _] => try apply factive_Content2 with (v:=e) in H2
  end.

Parameter _減らす : Event -> Prop.
Parameter _減量 : Event -> Prop.

Axiom causative_減らす : forall v : Event,
  _減量 v /\ _する v -> _減らす v.
Ltac solve_causative_減らす :=
  match goal with
    | [ H1 : _減量 ?e, H2 : _する ?e |- _ ]
     => apply causative_減らす with (v := e)
  end.

Parameter _開始 : Event -> Prop.
Parameter _始める : Event -> Prop.

Axiom causative_始める : forall v : Event,
  _開始 v /\ _する v -> _始める v.
Axiom causative_始める2 : forall (v1 : Event)(v2 : Event),
  _開始 v1 /\ _する v1 -> _始める v2.

Ltac solve_causative_始める :=
  match goal with
    | [ H1 : _開始 ?e, H2 : _する ?e |- _ ]
     => apply causative_始める with (v := e)
    | [ H1 : _開始 ?e, H2 : _する ?e, H3 : asEntity ?e2 = Acc ?e |- _始める ?e2 ]
     => apply causative_始める2 with (v1 := e)(v2 := e2)
  end.

Axiom causative_開始 : forall (v1 : Event)(v2 : Event),
  _開始 v1 /\ _する v1 -> _開始 v2 /\ _する v2.
Axiom causative_開始2 : forall (v1 : Event)(v2 : Event),
  asEntity v2 = Acc v1 ->  Acc v2 = asEntity v2.
Ltac solve_causative_開始 :=
  match goal with
    | [ H1 : _開始 ?e, H2 : _する ?e2, H3 : asEntity ?e2 = Acc ?e |- _開始 ?e2 ]
     => apply causative_開始 with (v1 := e)(v2 := e2)
    |[ H1 : _開始 ?e, H2 : _する ?e2, H3 : asEntity ?e2 = Acc ?e |- Acc ?e2 = asEntity ?e2 ]
     => apply causative_開始2 with (v1 := e)(v2 := e2)
  end.


Parameter _再開 : Event -> Prop.

Axiom causative_再開 : forall (v1 : Event)(v2 : Event),
  _再開 v1 /\ _する v1 -> _再開 v2 /\ _する v2.
Axiom causative_再開2 : forall (v1 : Event)(v2 : Event),
  asEntity v2 = Acc v1 ->  Acc v2 = asEntity v2.
Ltac solve_causative_再開 :=
  match goal with
    | [ H1 : _再開 ?e, H2 : _する ?e2, H3 : asEntity ?e2 = Acc ?e |- _再開 ?e2 ]
     => apply causative_再開 with (v1 := e)(v2 := e2)
    |[ H1 : _再開 ?e, H2 : _する ?e2, H3 : asEntity ?e2 = Acc ?e |- Acc ?e2 = asEntity ?e2 ]
     => apply causative_再開2 with (v1 := e)(v2 := e2)
  end.

Parameter _行う : Event -> Prop.

Axiom causative_する_なる : forall (v1 : Event)(v2 : Event)(F : Event -> Prop),
  F v1 /\ _する v1 -> F v2 /\ _する v2.
Axiom causative_する_なる2 : forall (v1 : Event)(v2 : Event),
  True ->  Acc v2 = Acc v1.
Ltac solve_causative_する_なる :=
  match goal with
    | [ H1 : ?a ?e, H2 : _する ?e, H3 : _なる ?e2 |- ?a ?e2 ]
     => apply causative_する_なる with (v1 := e)(v2 := e2)(F := a)
    | [ H1 : ?a ?e, H2 : _する ?e, H3 : _なる ?e2 |- _する ?e2 ]
     => apply causative_する_なる with (v1 := e)(v2 := e2)(F := a)
    |[ H1 : ?a ?e, H2 : _する ?e, H3 : _なる ?e2 |- Acc ?e2 = Acc ?e ]
     => apply causative_する_なる2 with (v1 := e)(v2 := e2)
    | [ H1 : ?a ?e, H2 : _する ?e, H3 : _行う ?e2 |- ?a ?e2 ]
     => apply causative_する_なる with (v1 := e)(v2 := e2)(F := a)
    | [ H1 : ?a ?e, H2 : _する ?e, H3 : _行う ?e2 |- _する ?e2 ]
     => apply causative_する_なる with (v1 := e)(v2 := e2)(F := a)
    |[ H1 : ?a ?e, H2 : _する ?e, H3 : _行う ?e2 |- Acc ?e2 = Acc ?e ]
     => apply causative_する_なる2 with (v1 := e)(v2 := e2)
  end.

Axiom causative_Dat : forall (v1 : Event)(v2 : Event)(F : Entity -> Prop),
   F (Dat v1) -> F (Dat v2).
Ltac solve_causative_Dat :=
  match goal with
    | [ H1 : ?a (Dat ?e), H2 : _する ?e, H3 : _なる ?e2 |- ?a (Dat ?e2) ]
     => apply causative_Dat with (v1 := e)(v2 := e2)(F := a)
  end.

Parameter _継続 : Event -> Prop.
Parameter _続ける : Event -> Prop.
Axiom causative_続ける2 : forall (v1 : Event)(v2 : Event),
  _継続 v1 /\ _する v1 -> _続ける v2.
Ltac solve_causative_続ける2 :=
  match goal with
    | [ H1 : _継続 ?e, H2 : _する ?e, H3 : asEntity ?e2 = Acc ?e |- _続ける ?e2 ]
     => apply causative_続ける2 with (v1 := e)(v2 := e2)
  end.

Axiom causative_Mod : forall (v1 : Event)(v2 : Event)(x : Entity),
  Mod x v1 -> Mod x v2.
Ltac solve_causative_Mod :=
  match goal with
    | [ H1 : _開始 ?e1, H2 : Mod ?t ?e1, H3 : _する ?e2, H4 : _ため ?t, H5 : asEntity ?e2 = Acc ?e1 |- Mod ?t ?e2 ]
     => apply causative_Mod with (v1 := e1)(v2 := e2)(x := t)
    | [ H1 : _認める ?e1, H2 : _する ?e2, H3 : Mod ?t ?e1, H6 : asEntity ?e2 = Acc ?e1 |- Mod ?t ?e2 ]
     => apply causative_Mod with (v1 := e1)(v2 := e2)(x := t)
    | [ H1 : _なる ?e1, H2 : _する ?e2, H3 : Mod ?t ?e1 |- Mod ?t ?e2 ]
     => apply causative_Mod with (v1 := e1)(v2 := e2)(x := t)
  end.

Parameter _から : Event -> (Entity -> Prop).
Axiom causative_から : forall (v1 : Event)(v2 : Event)(x : Entity),
  _から v1 x -> _から v2 x.
Ltac solve_causative_から :=
  match goal with
    | [ H1 : _認める ?e1, H2 : _する ?e2, H3 : _から ?e1 ?t, H6 : asEntity ?e2 = Acc ?e1 |- _から ?e2 ?t ]
     => apply causative_から with (v1 := e1)(v2 := e2)(x := t)
  end.

Parameter _著名 : Event -> Prop.
Axiom causative_Nom_Rel : forall (v : Event)(x : Entity),
  Rel x (Nom v) -> Nom v = x.
Ltac solve_causative_Nom_Rel :=
  match goal with
    | [ H1 : _著名 ?e, H2 : Rel ?t (Nom ?e) |- Nom ?e = ?t ] => apply causative_Nom_Rel with (v := e)(x := t)
    | [ H1 : _する ?e, H2 : Rel ?t (Nom ?e) |- Nom ?e = ?t ] => apply causative_Nom_Rel with (v := e)(x := t)
  end.

Parameter _に対して : Event -> (Entity -> Prop).
Axiom causative_に対して : forall (v1 : Event)(v2 : Event)(x : Entity),
  _に対して v1 x -> _に対して v2 x.
Ltac solve_causative_に対して :=
  match goal with
    | [ H1 : _開始 ?e1, H2 : _する ?e1, H3 : _に対して ?e1 ?t, H4 : _する ?e2, H5 : asEntity ?e2 = Acc ?e1 |- _に対して ?e2 ?t ]
     => apply causative_に対して with (v1 := e1)(v2 := e2)(x := t)
    | [ H2 : _する ?e1, H3 : _に対して ?e1 ?t, H4 : _する ?e2 |- _に対して ?e2 ?t ]
     => apply causative_に対して with (v1 := e1)(v2 := e2)(x := t)
  end.

Parameter _両側 : Entity -> Prop.
Parameter _片側 : Entity -> Prop.
Axiom causative_両側 : forall x : Entity,
  _両側 x -> _片側 x.
Ltac solve_causative_両側 :=
  match goal with
    | [ H1 : _両側 ?e |-  _片側 ?e ]
     => apply causative_両側 with (x := e)
  end.

Parameter _両 : Entity -> Prop.
Parameter _右 : Entity -> Prop.
Axiom causative_両_右 : forall x : Entity,
  _両 x -> _右 x.
Ltac solve_causative_両_右 :=
  match goal with
    | [ H1 : _両 ?t1, H2 : Rel ?t2 ?t1 |-  _右 ?t1 ]
     => apply causative_両_右 with (x := t1)
  end.

Parameter _左 : Entity -> Prop.
Axiom causative_両_左 : forall x : Entity,
  _両 x -> _左 x.
Ltac solve_causative_両_左 :=
  match goal with
    | [ H1 : _両 ?t1, H2 : Rel ?t2 ?t1 |-  _左 ?t1 ]
     => apply causative_両_左 with (x := t1)
  end.

(* Preliminary tactics *)

Ltac apply_ent :=
  match goal with
    | [x : Entity, H : forall x : Entity, _ |- _]
     => apply H; clear H
  end.

Ltac eqlem_sub :=
  match goal with
    | [ H1: ?A ?t, H2: forall x, @?D x -> @?C x |- _ ]
     => match D with context[ A ]
         => assert(C t); try (apply H2 with (x:= t)); clear H2
    end
  end.

Axiom unique_role : forall v1 v2 : Event, Nom v1 = Nom v2 -> v1 = v2.
Ltac resolve_unique_role :=
  match goal with
    H : Nom ?v1 = Nom ?v2 |- _
    => repeat apply unique_role in H
  end.

Ltac substitution :=
  match goal with
    | [H1 : _ = ?t |- _ ]
      => try repeat resolve_unique_role; try rewrite <- H1 in *; subst
    | [H1 : ?t = _ |- _ ]
      => try resolve_unique_role; try rewrite H1 in *; subst
  end.

Ltac exchange :=
  match goal with
    | [H1 : forall x, _, H2 : forall x, _ |- _]
     => generalize dependent H2
  end.

Ltac exchange_equality :=
  match goal with
    | [H1 : _ = _, H2: _ =  _ |- _]
     => generalize dependent H2
  end.

Ltac clear_pred :=
  match goal with
    | [H1 : ?F ?t, H2 : ?F ?u |- _ ]
     => clear H2
  end.

Ltac solve_false :=
  match goal with
    | [H : _ -> False |- False]
     => apply H
  end.

(* Main tactics *)

Ltac nltac_init :=
  try(intuition;
      try solve_false;
      repeat (subst || firstorder)).

Ltac nltac_base :=
  try nltac_init;
  try (eauto; eexists; firstorder);
  try (subst; eauto; firstorder; try congruence).

Ltac nltac_axiom :=
  try first
   [solve_factive_AccI |
    solve_たしか |
    solve_本当 |
    solve_嘘 |
    solve_Poss |
    solve_疑う_思う |
    solve_成功 |
    solve_factive_見る |
    solve_factive_聞く |
    solve_privative_former |
    solve_privative_fake |
    solve_anti_veridical_ほぼ |
    solve_anti_veridical_損ねる |
    solve_causative_破く_破れる |
    solve_causative_閉める_閉まる |
    solve_antonym_大きな_小さな |
    solve_antonym_おいしい_まずい |
    solve_antonym_開く_閉まる |
    solve_causative_減らす |
    solve_causative_始める |
    solve_causative_続ける2 |
    solve_causative_Mod |
    solve_causative_Dat |
    solve_causative_開始 |
    solve_causative_再開 |
    solve_causative_する_なる |
    solve_causative_から |
    solve_causative_Nom_Rel |
    solve_causative_に対して |
    solve_causative_両側 |
    solve_causative_両_右|
    solve_causative_両_左|
    solve_Content |
    solve_Content2
   ].

Ltac nltac_closure_axiom :=
 try first
   [solve_closure_見る |
    solve_closure_聞く |
    solve_closure_wouldbe
   ].

Ltac nltac_set :=
  repeat (nltac_init;
          try repeat substitution;
          try exchange_equality;
          try repeat substitution;
          (* try apply_ent; *)
          try eqlem_sub).

Ltac nltac_set_exch :=
  repeat (nltac_init;
          try repeat substitution;
          try apply_ent;
          try exchange;
          try eqlem_sub).

Ltac nltac_final :=
  try solve [repeat nltac_base | clear_pred; repeat nltac_base].

Ltac nltac_prove :=
  try solve [nltac_set; nltac_final | nltac_set_exch; nltac_final].

Ltac solve_gq1 :=
  match goal with
    H : Most _ _ |- _
    => let H0 := fresh in
       try solve [
          pose (H0 := H); eapply most_ex_import in H0; nltac_prove |
          pose (H0 := H); eapply most_consv in H0; eapply most_rightup; nltac_prove |
          pose (H0 := H); eapply most_consv in H0; nltac_prove |
          pose (H0 := H); eapply most_rightup in H0; nltac_prove ]
  end.

Ltac solve_gq2 :=
  match goal with
    H : Few _ |- _
    => let H0 := fresh in
       try solve [
          pose (H0 := H); eapply few_down in H0; nltac_prove ]
  end.

Ltac nltac :=
  firstorder;
  repeat (nltac_init || nltac_axiom || nltac_base);
  try repeat solve
    [nltac_prove |
     repeat nltac_init; (solve_gq1 || solve_gq2) |
     nltac_set; repeat nltac_axiom; solve [nltac_final | nltac_prove] |
     nltac_set; nltac_base; try nltac_closure_axiom; solve [nltac_final | nltac_prove]
    ].
